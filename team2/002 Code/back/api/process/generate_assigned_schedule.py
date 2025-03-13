from api.process.assign_classes import assign_classes
from api.process.match_classroom_type import match_classroom_type
from api.process.preprocess_offers import preprocess_offers


def generate_assigned_schedule(df_final, offer):
    """
    Generates the assigned schedule by processing offers and matching them with available rooms.

    Parameters:
        df_final (pd.DataFrame): The processed resource room DataFrame.
        offer (pd.DataFrame): The course offer DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the final class assignments.
    """
    # Step 1: Determine the maximum room capacity from the resource room DataFrame
    max_room_capacity = df_final['Capacity'].astype(int).max()

    # Step 2: Process the offers by expanding them based on room capacity
    offer = preprocess_offers(offer, max_room_capacity)

    print(df_final.columns)
    # Step 3: Align the room types and offer categories for matching
    df_final, offer = match_classroom_type(df_final, offer)

    # Step 4: Assign classes based on the constructed cost matrix and constraints
    assigned_schedule = assign_classes(df_final, offer)

    return assigned_schedule