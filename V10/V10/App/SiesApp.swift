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
                        
                        LiveFitZoneView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Live", systemImage: "chart.bar.fill")
                            }
                        
                        ChatView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Ask AI", systemImage: "bubble.left.and.bubble.right.fill")
                            }
                        
                        AccountScreen()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Account", systemImage: "person")
                            }
                    }
                }
            }
        }
    }
} 
