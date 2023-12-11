from queue import Queue

# Create a queue
my_queue = Queue()

while True:
    # Ask the user to input a value
    user_input = input("Enter a value (type 'q' to stop): ")

    # Check if the user wants to exit
    if user_input.lower() == 'q':
        print("Exiting the program.")
        break


    # Get the last element without removing it
    print(f"Size of the queue {(my_queue.empty())}")
    if my_queue.empty():
        my_queue.put(user_input)

        continue
    else:
        last_element = my_queue.queue[-1]

        print(f" last_element : {last_element}")
        print(f" user_element : {user_input}")



        # Check if the last value put is different from the front element
        if last_element != user_input:
            my_queue.put(user_input)

            print("Last value put is the different as the front element.")

            # my_queue.get()
        else:
            print("Last value put is the same as the front element.")
