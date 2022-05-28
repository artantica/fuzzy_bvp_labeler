from src.create_dataset import get_possible_samples, create_batches


if __name__ == '__main__':
    possible_samples_df = get_possible_samples()
    create_batches(possible_samples_df)

