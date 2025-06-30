import SwiftUI

@main
struct SiesApp: App {
    @StateObject private var userSettings = UserSettings()
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    
    var body: some Scene {
        WindowGroup {
            NavigationView {
                if !hasCompletedOnboarding {
                    HomeView()
                        .environmentObject(userSettings)
                        .onAppear {
                            // For development, auto-complete onboarding
                            #if DEBUG
                            hasCompletedOnboarding = true
                            #endif
                        }
                } else {
                    TabView {
                        ScanTab()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Scan", systemImage: "camera")
                            }
                        
                        ClosetListView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Closet", systemImage: "tshirt")
                            }
                        
                        UserMeasurementProfileView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Fit", systemImage: "ruler")
                            }
                        
                        ShopView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Shop", systemImage: "bag")
                            }
                        
                        MoreView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("More", systemImage: "ellipsis")
                            }
                    }
                }
            }
        }
    }
} 
