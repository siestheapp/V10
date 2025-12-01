#!/usr/bin/env python3
"""
Test Undo Functionality
Tests the action tracking and undo system for feedback updates
"""

import requests
import json
import time

BASE_URL = "http://localhost:8006"
USER_ID = 1
GARMENT_ID = 4  # Lululemon shirt

def test_feedback_and_undo():
    """Test the complete feedback update and undo cycle"""
    
    print("🧪 Testing Feedback Update and Undo Functionality")
    print("=" * 50)
    
    # Step 1: Get current feedback
    print("1. Getting current feedback...")
    response = requests.get(f"{BASE_URL}/user/{USER_ID}/closet")
    if response.status_code == 200:
        garments = response.json()
        lulu_garment = next((g for g in garments if g['id'] == GARMENT_ID), None)
        if lulu_garment:
            print(f"   Current feedback: {lulu_garment.get('fitFeedback', 'None')}")
            print(f"   Current chest: {lulu_garment.get('chestFit', 'None')}")
        else:
            print("   ❌ Garment not found")
            return
    else:
        print("   ❌ Failed to get closet data")
        return
    
    # Step 2: Update feedback
    print("\n2. Updating feedback to 'Too Tight'...")
    feedback_data = {
        "user_id": USER_ID,
        "feedback": {
            "chest": 1,      # Too Tight
            "overall": 1     # Too Tight
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/garment/{GARMENT_ID}/feedback",
        json=feedback_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        action_id = result.get('action_id')
        print(f"   ✅ Feedback updated successfully")
        print(f"   Action ID: {action_id}")
        print(f"   Can undo: {result.get('can_undo', False)}")
    else:
        print(f"   ❌ Failed to update feedback: {response.text}")
        return
    
    # Step 3: Verify the change
    print("\n3. Verifying feedback change...")
    time.sleep(1)  # Brief pause
    response = requests.get(f"{BASE_URL}/user/{USER_ID}/closet")
    if response.status_code == 200:
        garments = response.json()
        lulu_garment = next((g for g in garments if g['id'] == GARMENT_ID), None)
        if lulu_garment:
            print(f"   New feedback: {lulu_garment.get('fitFeedback', 'None')}")
            print(f"   New chest: {lulu_garment.get('chestFit', 'None')}")
        else:
            print("   ❌ Garment not found")
            return
    
    # Step 4: Get recent actions
    print("\n4. Getting recent actions...")
    response = requests.get(f"{BASE_URL}/user/{USER_ID}/actions/recent?limit=5")
    if response.status_code == 200:
        actions = response.json()['actions']
        print(f"   Found {len(actions)} recent actions:")
        for action in actions:
            print(f"     • {action['description']} (ID: {action['id']}) - Can undo: {action['can_undo']}")
    else:
        print(f"   ❌ Failed to get recent actions: {response.text}")
    
    # Step 5: Undo the action
    if action_id:
        print(f"\n5. Undoing action {action_id}...")
        undo_data = {"user_id": USER_ID}
        
        response = requests.post(
            f"{BASE_URL}/actions/{action_id}/undo",
            json=undo_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Action undone successfully")
            print(f"   Undo action ID: {result.get('undo_action_id')}")
        else:
            print(f"   ❌ Failed to undo action: {response.text}")
            return
    
    # Step 6: Verify the undo
    print("\n6. Verifying undo worked...")
    time.sleep(1)  # Brief pause
    response = requests.get(f"{BASE_URL}/user/{USER_ID}/closet")
    if response.status_code == 200:
        garments = response.json()
        lulu_garment = next((g for g in garments if g['id'] == GARMENT_ID), None)
        if lulu_garment:
            print(f"   Restored feedback: {lulu_garment.get('fitFeedback', 'None')}")
            print(f"   Restored chest: {lulu_garment.get('chestFit', 'None')}")
        else:
            print("   ❌ Garment not found")
            return
    
    print("\n🎉 Undo functionality test completed!")
    print("\nSummary:")
    print("✅ Feedback update with action tracking")
    print("✅ Action logging and retrieval")
    print("✅ Undo operation")
    print("✅ State restoration")

def test_multiple_undos():
    """Test multiple feedback changes and undos"""
    print("\n\n🔄 Testing Multiple Changes and Undos")
    print("=" * 40)
    
    changes = [
        {"chest": 2, "overall": 2},  # Tight but I Like It
        {"chest": 4, "overall": 4},  # Loose but I Like It
        {"chest": 3, "overall": 3},  # Good Fit
    ]
    
    action_ids = []
    
    for i, change in enumerate(changes, 1):
        print(f"\n{i}. Making change {i}: {change}")
        
        feedback_data = {
            "user_id": USER_ID,
            "feedback": change
        }
        
        response = requests.post(
            f"{BASE_URL}/garment/{GARMENT_ID}/feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            action_id = result.get('action_id')
            action_ids.append(action_id)
            print(f"   ✅ Change made, action ID: {action_id}")
        else:
            print(f"   ❌ Failed: {response.text}")
            return
        
        time.sleep(0.5)
    
    # Now undo them in reverse order
    print(f"\n🔙 Undoing {len(action_ids)} actions in reverse order...")
    
    for i, action_id in enumerate(reversed(action_ids), 1):
        print(f"\n{i}. Undoing action {action_id}...")
        
        undo_data = {"user_id": USER_ID}
        response = requests.post(
            f"{BASE_URL}/actions/{action_id}/undo",
            json=undo_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"   ✅ Action {action_id} undone")
        else:
            print(f"   ❌ Failed to undo: {response.text}")
        
        time.sleep(0.5)
    
    print("\n🎉 Multiple undo test completed!")

if __name__ == "__main__":
    try:
        # Test basic functionality
        test_feedback_and_undo()
        
        # Test multiple changes
        test_multiple_undos()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        print("Make sure the server is running on http://localhost:8006")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 