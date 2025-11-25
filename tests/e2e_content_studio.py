import time
from playwright.sync_api import sync_playwright

def run_tests():
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("Loading Dashboard...")
            page.goto("http://localhost:5173")
            page.wait_for_selector("h1:has-text('Welcome back')", timeout=10000)
            
            # Navigate to Social
            print("Navigating to Social...")
            page.click("h3:has-text('Social Media')")
            page.wait_for_url("**/social", timeout=5000)
            print(f"Current URL: {page.url}")
            
            # Check for Content Studio Tab
            print("Checking for Content Studio Tab...")
            # Use a more specific selector or wait for it
            page.wait_for_selector("button:has-text('Content Studio')", timeout=5000)
            studio_tab = page.locator("button:has-text('Content Studio')")
            if studio_tab.is_visible():
                results.append({"Test Case": "Content Studio Tab", "Status": "PASS", "Notes": "Tab visible"})
            else:
                results.append({"Test Case": "Content Studio Tab", "Status": "FAIL", "Notes": "Tab not found"})
                # return # Don't return, let it fail gracefully or print results

                
            # Click Tab
            studio_tab.click()
            
            # Check for Inputs
            print("Checking Studio Inputs...")
            topic_input = page.locator("textarea[placeholder*='The future of AI']")
            if topic_input.is_visible():
                results.append({"Test Case": "Topic Input", "Status": "PASS", "Notes": "Input visible"})
            else:
                results.append({"Test Case": "Topic Input", "Status": "FAIL", "Notes": "Input not found"})
            
            # Enter Topic
            print("Entering Topic...")
            topic_input.fill("Cyberpunk City")
            
            # Click Generate
            print("Clicking Generate...")
            generate_btn = page.locator("button:has-text('Generate Content')")
            generate_btn.click()
            
            # Wait for Generation (Long timeout for image gen)
            print("Waiting for Generation (up to 30s)...")
            # We expect it to switch back to dashboard tab automatically on success
            # So we wait for the composer textarea to be visible and have content
            
            # Wait for switch back to dashboard tab (Composer visible)
            page.wait_for_selector("textarea[placeholder*='What\\'s happening']", timeout=30000)
            
            # Check content
            composer = page.locator("textarea[placeholder*='What\\'s happening']")
            content = composer.input_value()
            if len(content) > 10:
                results.append({"Test Case": "Draft Generation", "Status": "PASS", "Notes": f"Draft generated: {content[:20]}..."})
            else:
                results.append({"Test Case": "Draft Generation", "Status": "FAIL", "Notes": "Draft empty"})
                
            # Check Image
            print("Checking for Generated Image...")
            img = page.locator("img[alt='Generated']")
            if img.is_visible():
                results.append({"Test Case": "Image Generation", "Status": "PASS", "Notes": "Image visible"})
            else:
                results.append({"Test Case": "Image Generation", "Status": "FAIL", "Notes": "Image not found"})
                
        except Exception as e:
            results.append({"Test Case": "Content Studio Flow", "Status": "ERROR", "Notes": str(e)})
        
        browser.close()
        
    # Print Table
    print("| Test Case | Status | Notes |")
    print("|---|---|---|")
    for res in results:
        print(f"| {res['Test Case']} | {res['Status']} | {res['Notes']} |")

if __name__ == "__main__":
    run_tests()
