import SwiftUI

@main
struct SiesApp: App {
    // Add this flag for development
    let skipToCloset = true  // Set to false before production
    
    var body: some Scene {
        WindowGroup {
            if skipToCloset {
                NavigationView {
                    ClosetView()  // Change back to ClosetView
                }
            } else {
                HomeView()  // Normal flow
            }
        }
    }
} 
