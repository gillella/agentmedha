import time
from playwright.sync_api import sync_playwright
import sys

def run_tests():
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Test 1: Load Dashboard
        try:
            print("Loading Dashboard...")
            page.goto("http://localhost:5173")
            page.wait_for_selector("h1:has-text('Welcome back')", timeout=5000)
            results.append({"Test Case": "Load Dashboard", "Status": "PASS", "Notes": "Dashboard loaded successfully"})
        except Exception as e:
            results.append({"Test Case": "Load Dashboard", "Status": "FAIL", "Notes": str(e)})
            
        # Test 2: Check Dashboard Cards
        cards = [
            "Social Media",
            "Email Priority",
            "Habitat Status",
            "Dependent Care",
            "Financial Overview"
        ]
        
        for card in cards:
            try:
                # Look for h3 with card title
                locator = page.locator(f"h3:has-text('{card}')")
                if locator.count() > 0:
                    results.append({"Test Case": f"Card: {card}", "Status": "PASS", "Notes": "Card visible"})
                else:
                    results.append({"Test Case": f"Card: {card}", "Status": "FAIL", "Notes": "Card not found"})
            except Exception as e:
                results.append({"Test Case": f"Card: {card}", "Status": "ERROR", "Notes": str(e)})

        # Test 3: Navigation (Social Media)
        try:
            page.click("h3:has-text('Social Media')")
            page.wait_for_url("**/social", timeout=2000)
            if "/social" in page.url:
                results.append({"Test Case": "Navigation: Social Media", "Status": "PASS", "Notes": "Navigated to /social"})
            else:
                results.append({"Test Case": "Navigation: Social Media", "Status": "FAIL", "Notes": f"URL mismatch: {page.url}"})
            
            # Go back
            page.go_back()
        except Exception as e:
             results.append({"Test Case": "Navigation: Social Media", "Status": "FAIL", "Notes": str(e)})

        # Test 4: Command Bar Presence
        try:
            if page.locator("input.command-input").is_visible():
                results.append({"Test Case": "Command Bar UI", "Status": "PASS", "Notes": "Input field visible"})
            else:
                results.append({"Test Case": "Command Bar UI", "Status": "FAIL", "Notes": "Input field not found"})
        except Exception as e:
            results.append({"Test Case": "Command Bar UI", "Status": "ERROR", "Notes": str(e)})
            
        # Test 5: Command Submission (Check for network request)
        try:
            print("Testing Command Submission...")
            # We want to see if a POST request is made to /api/chat or similar
            request_made = False
            def handle_request(request):
                nonlocal request_made
                # print(f"Request: {request.url} {request.method}")
                if "/chat" in request.url and request.method == "POST":
                    request_made = True
            
            page.on("request", handle_request)
            
            print("Filling input...")
            page.fill("input.command-input", "Hello Agent")
            print("Pressing Enter...")
            page.press("input.command-input", "Enter")
            
            # Wait a bit
            print("Waiting for network...")
            page.wait_for_timeout(2000)
            
            if request_made:
                results.append({"Test Case": "Command Submission", "Status": "PASS", "Notes": "Network request detected"})
            else:
                results.append({"Test Case": "Command Submission", "Status": "FAIL", "Notes": "No network request detected"})
                
        except Exception as e:
            results.append({"Test Case": "Command Submission", "Status": "ERROR", "Notes": str(e)})

        browser.close()
        
    # Print Table
    print("| Test Case | Status | Notes |")
    print("|---|---|---|")
    for res in results:
        print(f"| {res['Test Case']} | {res['Status']} | {res['Notes']} |")

if __name__ == "__main__":
    run_tests()
