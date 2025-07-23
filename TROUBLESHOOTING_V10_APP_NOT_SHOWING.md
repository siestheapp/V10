# Troubleshooting: V10 App Not Showing Up in Xcode "Choose an App to Run"

If your V10 app is missing from the "Choose an app to run" dialog in Xcode, follow these steps to resolve the issue:

---

## 1. **Check Your Scheme**
- At the top of Xcode, make sure the scheme is set to your app (e.g., `V10`), not a Swift file or view.
- The scheme should have a blue app icon, not a Swift file icon.
- If you see a view or file (like `GarmentFeedbackView`) selected, switch to the main app target.

## 2. **Edit Scheme Executable**
- Go to **Product > Scheme > Edit Scheme...**
- Under the **Run** section, set **Executable** to your app (e.g., `V10.app`).
- If it says "Ask on Launch," change it to your app.
- If your app is not listed, continue with the next steps.

## 3. **Check for Info.plist**
- Your app must have an `Info.plist` file in the main app directory (e.g., `ios_app/V10/Info.plist`).
- If missing, create a new Property List file named `Info.plist` and add the required keys:
  - `CFBundleIdentifier` (String, e.g., `com.yourcompany.V10`)
  - `CFBundleName` (String, e.g., `V10`)
  - `CFBundleExecutable` (String, `$(EXECUTABLE_NAME)`)
  - `CFBundlePackageType` (String, `APPL`)
  - `LSRequiresIPhoneOS` (Boolean, `YES`)
  - `UILaunchScreen` (String, `LaunchScreen`)
  - `CFBundleShortVersionString` (String, `1.0`)
  - `CFBundleVersion` (String, `1`)
- In your target's **Build Settings**, set the "Info.plist File" path to the correct location.

## 4. **Remove Info.plist from Copy Bundle Resources**
- Select your project > target > **Build Phases** > **Copy Bundle Resources**.
- If `Info.plist` is listed here, remove it (it should NOT be copied as a resource).

## 5. **Clean and Rebuild**
- **Product > Clean Build Folder** (⇧⌘K)
- **Build** (⌘B)
- **Run** (⌘R)

## 6. **Restart Xcode and Simulator**
- Quit both Xcode and the simulator completely.
- Reopen Xcode, select your app and simulator, and try to run again.

## 7. **Check for Build Errors**
- If the build fails, check the Issue Navigator (red ❌ icon) for errors.
- Fix any errors related to missing Info.plist, duplicate files, or scheme issues.

## 8. **Check @main in App.swift**
- Make sure your app entry point (e.g., `SiesApp.swift` or `V10App.swift`) has the `@main` attribute:
  ```swift
  @main
  struct V10App: App {
      var body: some Scene {
          WindowGroup {
              ContentView() // or your starting view
          }
      }
  }
  ```
- Without `@main`, Xcode will not recognize your app as runnable.

## 9. **Try a New Simulator or Scheme**
- Add a new simulator in **Window > Devices and Simulators**.
- Try creating a new scheme in **Product > Scheme > New Scheme...**.

---

## **Summary Checklist**
- [ ] Scheme is set to your app (not a file or view)
- [ ] Executable in scheme is set to your app
- [ ] Info.plist exists and is configured
- [ ] Info.plist is NOT in Copy Bundle Resources
- [ ] Cleaned and rebuilt the project
- [ ] @main is present in your app entry point
- [ ] No build errors

If you follow these steps and your app still does not appear, double-check your project structure and target membership, or try restarting your Mac. 