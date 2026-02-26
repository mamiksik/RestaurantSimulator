import json
import random
import textwrap
import warnings
from typing import Literal

from openai.types.chat import ChatCompletion

from RestaurantSimulator.simulator.chatbot import StatefulChatbot, ExtractedAnswers
import RestaurantSimulator.models as models

from datetime import datetime
from django.utils.timezone import make_aware


# gpt-5-nano is somewhat cheaper per token, but for our use case we
# observed is costs about 2x tokens per request (bizarre pricing)
MODEL_DECODERS = "gpt-4.1-nano"
MODEL_WAITER = "gpt-4o-mini"
MODEL_CUSTOMER = "gpt-4o-mini"


def create_message_from_openai_response(
    *,
    on: models.SimulatedChatThread,
    role: Literal["WaiterBot", "CustomerBot"],
    temp: float,
    msg: ChatCompletion,
):
    on.messages.create(
        role=role,
        content=msg.choices[0].message.content,
        timestamp=make_aware(datetime.fromtimestamp(msg.created)),
        completion_tokens=msg.usage.completion_tokens,
        prompt_tokens=msg.usage.prompt_tokens,
        total_tokens=msg.usage.total_tokens,
        model=msg.model,
        temperature=temp,
    )


def generate_customer_bot_prompt() -> str:
    hunger_levels = random.choice(
        [
            "not hungry at all",
            "a little hungry",
            "somewhat hungry",
            "very hungry",
            "extremely hungry",
        ]
    )

    mood = random.choice(["great", "good", "okay", "bad", "terrible"])

    dietary_preferences = random.choice(
        ["Omnivore", "Pescatarian", "Vegetarian", "Vegan"]
    )
    favorite_cuisines = random.choice(
        [
            "Italian",
            "Chinese",
            "Mexican",
            "Indian",
            "American",
            "Mediterranean",
            "Japanese",
            "Thai",
        ]
    )

    fan_of = random.choice(
        [
            "",
            "You like to eat comfort food.",
            "You like to eat underrated food.",
            "You like to eat street food.",
            "You like to eat gourmet food.",
            "You like to eat your childhood favourite dishes.",
        ]
    )

    avoid_foods = random.choice(
        # Only apply this modifier in 1/2 of the cases
        [
            "",
            f"When ask about food you like avoid naming "
            f"any of the {random.choice([10, 15, 20])} most common foods in {favorite_cuisines} cuisine",
        ]
    )

    return textwrap.dedent(f"""\
        You are role-playing as a customer at a restaurant. You are in a {mood} mood and {hunger_levels}. 
        You are {dietary_preferences} and your favorite cuisine is {favorite_cuisines}. {fan_of} {avoid_foods}
        
        Your task is to respond to the waiter's questions. Keep the answers concise but informative. Do not ask 
        the waiter any questions, just respond to their questions. Your answer must align with the tastes profile of 
        the persona you are role playing and their current mood and appetite.
        
        For example, if you are a vegetarian and like Italian, you might answer the waiter's 
        questions like:
        "I am a vegetarian and I love Italian food" 
        or "My top 3 favorite foods are Margherita Pizza, Caprese Salad, and Eggplant Parmesan" 
        or "Today, I would like to order the Margherita Pizza."
        
        Or for example, if you are a little hungry pescatarian who likes street food: 
        "I would like to order Fish and Chips"
        Or for example, if Omnivore who doesn't like any of the 10 ten most common omnivore dishes:
        "My 3 favourite dishes are: Baked Duck, Larb khua mu and Bibimbap 
    """)


def extract_answers(customer_answer: ChatCompletion) -> ExtractedAnswers:
    customer_answer: str = customer_answer.choices[0].message.content

    top3_processor = StatefulChatbot(
        model=MODEL_DECODERS,
        system_prompt=textwrap.dedent("""\
            Your task is extract the top 3 favorite foods from users text. Return the answer as a JSON array of strings, 
            with each string being one of the top 3 favorite foods. Do not output anything other than the JSON array. 
            If you cannot find 3 favorite foods, return as many as you can find, but still in an array format. 
            
            For example, if the user says "I love pizza and pasta", you might return ["pizza", "pasta"]. 
            If the user says "I really like sushi", you might return ["sushi"].
        """),
    )

    top3_dishes_msg = top3_processor.send_user_message(customer_answer)
    top3_dishes = top3_dishes_msg.choices[0].message.content
    try:
        top3_dishes = json.loads(top3_dishes)
    except json.JSONDecodeError:
        top3_dishes = []
        warnings.warn(
            f"Failed to decode top 3 foods response as JSON. Original response was: {top3_dishes} from {top3_processor}"
        )

    print(f"Raw top 3 foods response: {top3_dishes}")

    diet_processor = StatefulChatbot(
        model=MODEL_DECODERS,
        system_prompt=textwrap.dedent("""\
            Your task is infer user dietary preference based on the food items they name. The possible dietary preferences are:
            "Omnivore", "Pescatarian", "Vegetarian", "Vegan". Return the answer as a single string that is one of these 4 options. 
            Do not output anything other than the dietary preference string. If you cannot determine the user's dietary preference, return "Unknown".
            
            For example, if the user says "I would like to order Pizza Margarita", you might return "Vegetarian". 
            If the user says "I will order fish and chips", you might return "Pescatarian". 
            If the user says "I want to order steak", you might return "Omnivore".
        """),
    )

    diet_msg = diet_processor.send_user_message(customer_answer)
    diet = diet_msg.choices[0].message.content
    if diet not in ["Omnivore", "Pescatarian", "Vegetarian", "Vegan", "Unknown"]:
        warnings.warn(f"Unexpected dietary preference response: {diet} from {diet}")
        diet = "Unknown"

    print(f"Raw dietary preference response: {diet}")

    return ExtractedAnswers(
        top3_dishes=top3_dishes,
        top3_usage=ExtractedAnswers.usage_to_dict(top3_dishes_msg.usage),
        top3_model=top3_dishes_msg.model,
        diet=diet,
        diet_usage=ExtractedAnswers.usage_to_dict(diet_msg.usage),
        diet_model=top3_dishes_msg.model,
    )


def print_exchange(*, waiter_msg: ChatCompletion, customer_msg: ChatCompletion):
    print(f"Waiter: {waiter_msg.choices[0].message.content}")
    print(f"Customer: {customer_msg.choices[0].message.content}")
    print("----")


def step4_waiter():
    waiter_prompt = textwrap.dedent("""\
        You are a friendly and professional restaurant waiter.
        Your role is to:
            1. Welcome customers warmly and ask about their day
            2. Ask about their top 3 favorite dishes
            3. Ask what dish(es) they want to order today

        Be conversational, warm, professional but concise. Always ask one question at a time and wait for the 
        customer's response before proceeding to the next question.
    """)

    waiter_temp = 1
    customer_temp = random.choice([1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4])
    customer_prompt = generate_customer_bot_prompt()
    waiter_bot = StatefulChatbot(
        model=MODEL_WAITER, system_prompt=waiter_prompt, temperature=waiter_temp
    )
    customer_bot = StatefulChatbot(
        model=MODEL_CUSTOMER, system_prompt=customer_prompt, temperature=customer_temp
    )
    chat_thread_db = models.SimulatedChatThread(
        waiter_prompt=waiter_prompt, customer_prompt=customer_prompt
    )

    # We need to safe here to have ID assign to our entity, so that we can reference it
    # In production app would wrap this in a transaction to prevent having partial records
    # in case the subsequent codes fails
    chat_thread_db.save()

    # Step 1
    waiter_welcomes_customer = waiter_bot.send_message()
    create_message_from_openai_response(
        on=chat_thread_db,
        role="WaiterBot",
        temp=waiter_temp,
        msg=waiter_welcomes_customer,
    )

    customer_reply = customer_bot.send_user_message(
        waiter_welcomes_customer.choices[0].message.content
    )
    create_message_from_openai_response(
        on=chat_thread_db, role="CustomerBot", temp=customer_temp, msg=customer_reply
    )

    print_exchange(waiter_msg=waiter_welcomes_customer, customer_msg=customer_reply)

    # Step 2
    waiter_asks_favorites = waiter_bot.send_user_message(
        customer_reply.choices[0].message.content
    )
    create_message_from_openai_response(
        on=chat_thread_db, role="WaiterBot", temp=waiter_temp, msg=waiter_asks_favorites
    )

    customer_shares_favorites = customer_bot.send_user_message(
        waiter_asks_favorites.choices[0].message.content
    )
    create_message_from_openai_response(
        on=chat_thread_db,
        role="CustomerBot",
        temp=customer_temp,
        msg=customer_shares_favorites,
    )

    print_exchange(
        waiter_msg=waiter_asks_favorites, customer_msg=customer_shares_favorites
    )

    # Step 2.1: Process answers
    extracted_answers = extract_answers(customer_shares_favorites)
    chat_thread_db.extracted_answers = extracted_answers.model_dump()

    # Step 3
    waiter_asks_order = waiter_bot.send_user_message(
        customer_shares_favorites.choices[0].message.content
    )
    create_message_from_openai_response(
        on=chat_thread_db, role="WaiterBot", temp=waiter_temp, msg=waiter_asks_order
    )

    customer_shares_order = customer_bot.send_user_message(
        waiter_asks_order.choices[0].message.content
    )
    create_message_from_openai_response(
        on=chat_thread_db,
        role="CustomerBot",
        temp=customer_temp,
        msg=customer_shares_order,
    )

    print_exchange(waiter_msg=waiter_asks_order, customer_msg=customer_shares_order)
    chat_thread_db.save()


if __name__ == "__main__":
    # step3_waiter()
    step4_waiter()
