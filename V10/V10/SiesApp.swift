import SwiftUI

@main
struct SiesApp: App {
    var body: some Scene {
        WindowGroup {
            NavigationStack {
                // Comment out the normal flow
                // UserStart()
                
                // Add direct access to ScanGarmentView for testing
                ScanGarmentView()
            }
        }
    }
} 
