import sys
from participant_identification import identify_participants, determine_winner
from mqtt_operations import (
    winner_becomes_aggregator,
    winner_creates_mqtt_broker,
    send_communication_link_to_others,
    receive_mqtt_broker_link,
    start_dfl_using_mqtt
    
)
from ml_operations import (
    train_machine_learning_model,
    send_model_to_aggregator,
    aggregator_receives_models,
    aggregate_models,
    is_model_better,
    post_training_steps,
    aggregator_saves_global_model_in_ipfs,
    disconnect_all_nodes,
    cleanup,
    aggregator_stops_mqtt_broker_service,
    send_global_model_to_others
)
from utils import get_global_ipfs_link

def pause_execution():
    if input("Press Enter to continue (or type 'q' and press Enter to quit): ").strip().lower() == 'q':
        sys.exit()

def main():
    print(identify_participants())
    pause_execution()
    
    if determine_winner():
        print(winner_creates_mqtt_broker())
        pause_execution()
        if send_communication_link_to_others():
            print(send_communication_link_to_others())
        else:
            print(receive_mqtt_broker_link())
        pause_execution()

    print(start_dfl_using_mqtt())
    global_ipfs_link = get_global_ipfs_link()
    print(winner_becomes_aggregator())
    pause_execution()

    while True:
        print(train_machine_learning_model())
        pause_execution()
        print(send_model_to_aggregator())
        pause_execution()
        print(aggregator_receives_models())
        pause_execution()
        print(aggregate_models())
        pause_execution()
        print(send_global_model_to_others())
        pause_execution()

        if is_model_better():
            continue
        else:
            break

    print(post_training_steps())
    if aggregator_saves_global_model_in_ipfs():
        print(aggregator_saves_global_model_in_ipfs())
    pause_execution()
    
    print(disconnect_all_nodes())
    pause_execution()
    
    print(cleanup())
    pause_execution()
    
    if aggregator_stops_mqtt_broker_service():
        print(aggregator_stops_mqtt_broker_service())
    pause_execution()

if __name__ == "__main__":
    main()