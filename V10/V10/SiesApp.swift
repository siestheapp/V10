import SwiftUI

@main
struct SiesApp: App {
    // Add this flag for development
    let skipToCloset = true  // Set to false before production
    
    var body: some Scene {
        WindowGroup {
            if skipToCloset {
                NavigationView {
                    ClosetView()
                }
            } else {
                HomeView()  // Normal flow
            }
        }
    }
} 
