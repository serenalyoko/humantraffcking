import pandas


def up_sample(df):
    # Separate majority and minority classes
    df_majority = df[df.label == 'safe']
    df_minority = df[df.label == 'risk']


    # Upsample minority class to 0.2 the size of majority class
    df_minority_upsampled = df_minority.sample(n=int(len(df_majority) * 0.2), replace=True, random_state=42)

    # Combine majority class with upsampled minority class and shuffle the order
    df_upsampled = pandas.concat([df_majority, df_minority_upsampled]).sample(frac=1, random_state=42).reset_index(drop=True)

    return df_upsampled

def print_df_spec(df):
    # check column names
    print("Column names:", df.columns.tolist())
    # check different labels in the dataset
    print("Unique labels:", df['label'].unique())
    # check number of rows with label risk and safe
    print("Number of 'risk' labels:", (df['label'] == 'risk').sum())
    print("Number of 'safe' labels:", (df['label'] == 'safe').sum())
    # check the size of the dataset
    print("Dataset size:", df.shape)

def down_sample(df):
    # Separate majority and minority classes
    df_majority = df[df.label == 'safe']
    df_minority = df[df.label == 'risk']
    # down sample majority class to match the size of minority class
    df_majority_downsampled = df_majority.sample(n=int(len(df_minority)*0.2), random_state=42)

    # Combine downsampled majority class with minority class
    df_downsampled = pandas.concat([df_majority_downsampled, df_minority]).sample(frac=1, random_state=42).reset_index(drop=True)

    return df_downsampled
def balanced_sample(df):
    # Separate majority and minority classes
    df_majority = df[df.label == 'safe']
    df_minority = df[df.label == 'risk']
    # down sample majority class to match the size of minority class
    df_majority_downsampled = df_majority.sample(n=len(df_minority), random_state=42)

    # Combine downsampled majority class with minority class
    df_balanced = pandas.concat([df_majority_downsampled, df_minority]).sample(frac=1, random_state=42).reset_index(drop=True)

    return df_balanced
if __name__ == "__main__":
    # Load the dataset
    df = pandas.read_csv("data/finalized_data.csv")
    print_df_spec(df)
    # Upsample the dataset
    df_upsampled = up_sample(df)
    print_df_spec(df_upsampled)
    # Save the upsampled dataset
    df_upsampled.to_csv("data/upsampled_data.csv", index=False)

    df_balanced = balanced_sample(df)
    print_df_spec(df_balanced)
    # Save the balanced dataset
    df_balanced.to_csv("data/balanced_data.csv", index=False)

