class Competition:
    def __init__(self, participants):
        self.participants = participants

    def determine_winner(self):
        winner = None
        best_performance = -1

        for participant in self.participants:
            performance = participant['score']

            if performance > best_performance:
                winner = participant
                best_performance = performance

        return winner

def main():
    participants = [
        {'name': 'Participant 1', 'score': 90},
        {'name': 'Participant 2', 'score': 85},
        {'name': 'Participant 3', 'score': 95},
    ]

    competition = Competition(participants)
    winner = competition.determine_winner()

    if winner:
        print(f"The winner is {winner['name']} with a score of {winner['score']}.")
    else:
        print("No winner found.")

if __name__ == "__main__":
    main()
