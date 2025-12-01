import psycopg2
from db_change_logger import log_user_creation, log_garment_addition, log_feedback_submission, log_brand_addition

# Database connection info (from db_snapshot.py)
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

def get_or_create_id(cursor, table, column, value, extra_columns=None, extra_values=None):
    # Try to find the ID
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    # Insert if not found
    if extra_columns and extra_values:
        columns = f"{column}, {', '.join(extra_columns)}"
        placeholders = ', '.join(['%s'] * (1 + len(extra_values)))
        values = (value,) + tuple(extra_values)
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id", values)
    else:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING id", (value,))
    new_id = cursor.fetchone()[0]
    
    # Log the creation if it's a brand
    if table == "brands":
        log_brand_addition(value, new_id)
    
    return new_id

def get_user_id(cursor, email):
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        return result[0]
    # If not found, prompt for info and print insert SQL
    print("User not found. Please create the user first.")
    gender = input("Enter gender for new user (Male/Female/Unisex): ")
    height = input("Enter height in inches (or leave blank): ")
    units = input("Preferred units (in/cm, default 'in'): ") or 'in'
    insert_sql = f"""
INSERT INTO users (email, gender{', height_in' if height else ''}, preferred_units)
VALUES ('{email}', '{gender}'{', ' + height if height else ''}, '{units}');
"""
    print("\n--- SQL to create user ---")
    print(insert_sql)
    print("After creating the user, re-run this script.")
    exit(1)

def get_feedback_code_id(cursor, feedback_text):
    cursor.execute("SELECT id FROM feedback_codes WHERE feedback_text = %s", (feedback_text,))
    result = cursor.fetchone()
    if result:
        return result[0]
    print(f"Feedback code '{feedback_text}' not found. Please add it first.")
    exit(1)

def get_size_guide_entry(cursor, brand_id, category_id, gender, fit_type, size_label, subcategory_id=None):
    # Try to find the size_guide_id
    if subcategory_id and subcategory_id != 'NULL':
        cursor.execute("""
            SELECT sge.* FROM size_guides sg
            JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            WHERE sg.brand_id = %s AND sg.category_id = %s AND sg.gender = %s AND sg.fit_type = %s
              AND sge.size_label = %s AND sg.subcategory_id = %s
            LIMIT 1
        """, (brand_id, category_id, gender, fit_type, size_label, subcategory_id))
    else:
        cursor.execute("""
            SELECT sge.* FROM size_guides sg
            JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            WHERE sg.brand_id = %s AND sg.category_id = %s AND sg.gender = %s AND sg.fit_type = %s
              AND sge.size_label = %s
            LIMIT 1
        """, (brand_id, category_id, gender, fit_type, size_label))
    return cursor.fetchone(), [desc[0] for desc in cursor.description]

def feedback_flow(cursor):
    print("\n=== Feedback Insert SQL Generator ===")
    user_garment_id = input("Enter user_garment_id for feedback: ")
    brand_name = input("Brand name: ")
    brand_id = get_or_create_id(cursor, "brands", "name", brand_name)
    category_name = input("Category name: ")
    category_id = get_or_create_id(cursor, "categories", "name", category_name)
    subcategory_name = input("Subcategory name (or leave blank): ")
    if subcategory_name:
        subcategory_id = get_or_create_id(cursor, "subcategories", "name", subcategory_name, ["category_id"], [category_id])
    else:
        subcategory_id = 'NULL'
    gender = input("Gender (Male/Female/Unisex): ")
    size_label = input("Size label: ")
    fit_type = input("Fit type: ")
    # Look up size guide entry
    entry, columns = get_size_guide_entry(cursor, brand_id, category_id, gender, fit_type, size_label, subcategory_id if subcategory_id != 'NULL' else None)
    feedback_dimensions = []
    if entry:
        entry_dict = dict(zip(columns, entry))
        for dim in ["chest", "waist", "sleeve", "neck", "hip", "length"]:
            min_col = f"{dim}_min"
            max_col = f"{dim}_max"
            range_col = f"{dim}_range"
            if (min_col in entry_dict and entry_dict[min_col] is not None) or \
               (max_col in entry_dict and entry_dict[max_col] is not None) or \
               (range_col in entry_dict and entry_dict[range_col]):
                feedback_dimensions.append(dim)
        feedback_dimensions = ["overall"] + feedback_dimensions
        print(f"\nFeedback will be collected for: {', '.join(feedback_dimensions)}")
    else:
        print("No size guide entry found for this garment. Only 'overall' feedback will be collected.")
        feedback_dimensions = ["overall"]
    for dim in feedback_dimensions:
        feedback_text = input(f"Feedback for {dim} (e.g. Good Fit, Too Tight): ")
        feedback_code_id = get_feedback_code_id(cursor, feedback_text)
        feedback_sql = f"""
INSERT INTO user_garment_feedback (
    user_garment_id, dimension, feedback_code_id
) VALUES (
    {user_garment_id}, '{dim}', {feedback_code_id}
);
"""
        print(f"\n--- SQL to insert feedback for {dim} ---")
        print(feedback_sql)
    print("\nDone. Copy and execute the above SQL in your database client.")

def main():
    print("=== Garment Input Helper for tailor3 ===")
    print("(This script generates SQL insert statements for user_garments and user_garment_feedback)")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("\nChoose mode:")
    print("1. Generate garment insert SQL (full flow)")
    print("2. Generate feedback insert SQL for an existing garment")
    mode = input("Enter 1 or 2: ").strip()
    if mode == '2':
        feedback_flow(cursor)
        cursor.close()
        conn.close()
        return
    # Full flow (garment + feedback)
    user_email = input("User email: ")
    user_id = get_user_id(cursor, user_email)
    brand_name = input("Brand name: ")
    brand_id = get_or_create_id(cursor, "brands", "name", brand_name)
    category_name = input("Category name: ")
    category_id = get_or_create_id(cursor, "categories", "name", category_name)
    subcategory_name = input("Subcategory name (or leave blank): ")
    if subcategory_name:
        subcategory_id = get_or_create_id(cursor, "subcategories", "name", subcategory_name, ["category_id"], [category_id])
    else:
        subcategory_id = 'NULL'
    gender = input("Gender (Male/Female/Unisex): ")
    size_label = input("Size label: ")
    fit_type = input("Fit type: ")
    product_name = input("Product name: ")
    product_url = input("Product URL: ")

    # Generate garment insert SQL
    garment_sql = f"""
INSERT INTO user_garments (
    user_id, brand_id, category_id, subcategory_id, gender, size_label, fit_type, unit, product_name, product_url, owns_garment
) VALUES (
    {user_id}, {brand_id}, {category_id}, {subcategory_id}, '{gender}', '{size_label}', '{fit_type}', 'in', '{product_name.replace("'", "''")}', '{product_url}', true
);
"""
    print("\n--- SQL to insert garment ---")
    print(garment_sql)

    # Optionally prompt for feedback
    add_feedback = input("Add feedback for this garment? (y/n): ").strip().lower()
    if add_feedback == 'y':
        print("\nAfter inserting the garment, look up the user_garment_id and re-run this script in feedback mode (option 2) to generate feedback SQL.")

    cursor.close()
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main() 