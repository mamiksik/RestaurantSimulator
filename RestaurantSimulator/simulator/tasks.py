import json
import random
import textwrap
import warnings

from RestaurantSimulator.simulator.chatbot import Chatbot, ExtractedAnswers
import RestaurantSimulator.models as models

from datetime import datetime
from django.utils.timezone import make_aware

def print_exchange(*, waiter_msg: str, customer_msg: str):
    print(f"Waiter: {waiter_msg}")
    print(f"Customer: {customer_msg}")
    print("----")

def extract_answers(customer_answer: str) -> ExtractedAnswers:
    top3_processor = Chatbot(
        model="gpt-4.1-nano",
        system_prompt=textwrap.dedent("""\
            Your task is extract the top 3 favorite foods from users text. Return the answer as a JSON array of strings, 
            with each string being one of the top 3 favorite foods. Do not output anything other than the JSON array. 
            If you cannot find 3 favorite foods, return as many as you can find, but still in an array format. 
            
            For example, if the user says "I love pizza and pasta", you might return ["pizza", "pasta"]. 
            If the user says "I really like sushi", you might return ["sushi"].
        """)
    )

    answer = top3_processor.send_user_message(customer_answer)
    try:
        top_3_foods_response = json.loads(answer)
    except json.JSONDecodeError:
        top_3_foods_response = []
        warnings.warn(f"Failed to decode top 3 foods response as JSON. Original response was: {answer} from {top3_processor}")

    print(f"Raw top 3 foods response: {top_3_foods_response}")

    dietary_preference_processor = Chatbot(
        model="gpt-4.1-nano",
        system_prompt=textwrap.dedent("""\
            Your task is infer user dietary preference based on the food items they name. The possible dietary preferences are:
            "Omnivore", "Pescatarian", "Vegetarian", "Vegan". Return the answer as a single string that is one of these 4 options. 
            Do not output anything other than the dietary preference string. If you cannot determine the user's dietary preference, return "Unknown".
            
            For example, if the user says "I would like to order Pizza Margarita", you might return "Vegetarian". 
            If the user says "I will order fish and chips", you might return "Pescatarian". 
            If the user says "I want to order steak", you might return "Omnivore".
        """)
    )

    dietary_preference_response = dietary_preference_processor.send_user_message(customer_answer)
    if dietary_preference_response not in ["Omnivore", "Pescatarian", "Vegetarian", "Vegan", "Unknown"]:
        warnings.warn(f"Unexpected dietary preference response: {dietary_preference_response} from {dietary_preference_processor}")
        dietary_preference_response = "Unknown"

    print(f"Raw dietary preference response: {dietary_preference_response}")

    return ExtractedAnswers(
        top_3_favorite_foods=top_3_foods_response,
        dietary_preference=dietary_preference_response
    )




def step4_waiter():
    model = "gpt-4o-mini"
    waiter_prompt = textwrap.dedent("""\
        You are a friendly and professional restaurant waiter.
        Your role is to:
            1. Welcome customers warmly and ask about their day
            2. Ask about their top 3 favorite foods
            3. Ask what dish(es) they want to order today

        Be conversational, warm, professional but concise. Always ask one question at a time and wait for the 
        customer's response before proceeding to the next question.
    """)

    dietary_preferences = ["Omnivore", "Pescatarian", "Vegetarian", "Vegan"]
    favorite_cuisines = ["Italian", "Chinese", "Mexican", "Indian", "American", "Mediterranean", "Japanese", "Thai"]

    mood = ["in a great mood", "in a good mood", "in an okay mood", "in a bad mood", "in a terrible mood"]
    hunger_levels = ["not hungry at all", "a little hungry", "somewhat hungry", "very hungry", "extremely hungry"]
    customer_prompt = textwrap.dedent(f"""\
        You are role-playing as a customer at a restaurant. You are {random.choice(mood)} and {random.choice(hunger_levels)}.
        Your dietary preference is {random.choice(dietary_preferences)} and your favorite cuisine is {random.choice(favorite_cuisines)}. 
        Your task is to respond to the waiter's questions. Keep the answers concise but informative. Do not ask the waiter 
        any questions, just respond to their questions. Your answer must align with your dietary preferences and favorite cuisine. 
        
        For example, if you are a vegetarian and your favorite cuisine is Italian, you might answer the waiter's questions like:
        "I am a vegetarian and I love Italian food" 
        or "My top 3 favorite foods are Margherita Pizza, Caprese Salad, and Eggplant Parmesan" 
        or "Today, I would like to order the Margherita Pizza."
    """)

    waiter = Chatbot(model=model, system_prompt=waiter_prompt)
    customer = Chatbot(model=model, system_prompt=customer_prompt)

    chat_thread_db = models.SimulatedChatThread(
        waiter_prompt=waiter_prompt,
        customer_prompt=customer_prompt
    )
    chat_thread_db.save()


    waiter_welcomes_customer = waiter.send_message()
    chat_thread_db.messages.create(
        role="WaiterBot", content=waiter_welcomes_customer, timestamp=make_aware(datetime.fromtimestamp(waiter.latest_response["timestamp"]))
    )

    customer_reply = customer.send_user_message(waiter_welcomes_customer)
    chat_thread_db.messages.create(
        role="CustomerBot", content=customer_reply, timestamp=make_aware(datetime.fromtimestamp(waiter.latest_response["timestamp"]))
    )

    print_exchange(waiter_msg=waiter_welcomes_customer, customer_msg=customer_reply)


    waiter_asks_favorites = waiter.send_user_message(customer_reply)
    chat_thread_db.messages.create(
        role="WaiterBot", content=waiter_asks_favorites, timestamp=make_aware(datetime.fromtimestamp(waiter.latest_response["timestamp"]))
    )

    customer_shares_favorites = customer.send_user_message(waiter_asks_favorites)
    chat_thread_db.messages.create(
        role="CustomerBot", content=customer_shares_favorites, timestamp=make_aware(datetime.fromtimestamp(waiter.latest_response["timestamp"]))
    )

    extracted_answers = extract_answers(customer_shares_favorites)
    chat_thread_db.extracted_answers = extracted_answers.model_dump()

    print_exchange(waiter_msg=waiter_asks_favorites, customer_msg=customer_shares_favorites)


    waiter_asks_order = waiter.send_user_message(customer_shares_favorites)
    chat_thread_db.messages.create(
        role="WaiterBot", content=waiter_asks_order, timestamp=make_aware(datetime.fromtimestamp(waiter.latest_response["timestamp"]))
    )

    customer_shares_order = customer.send_user_message(waiter_asks_order)
    chat_thread_db.messages.create(
        role="CustomerBot", content=customer_shares_order, timestamp=make_aware(datetime.fromtimestamp(waiter.latest_response["timestamp"]))
    )

    print_exchange(waiter_msg=waiter_asks_order, customer_msg=customer_shares_order)
    chat_thread_db.save()

if __name__ == "__main__":
    # step3_waiter()
    step4_waiter()