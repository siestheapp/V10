import SwiftUI

@main
struct SiesApp: App {
    @StateObject private var userSettings = UserSettings()
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    @State private var forceMainApp = false
    @State private var selectedTab = 0
    
    var body: some Scene {
        WindowGroup {
            if !hasCompletedOnboarding && !forceMainApp {
                NavigationView {
                    HomeView()
                        .environmentObject(userSettings)
                        .onAppear {
                            // For development, auto-complete onboarding faster
                            #if DEBUG
                            print("🚀 DEBUG: Skipping onboarding")
                            // TEMPORARILY DISABLED TO RECREATE DILAWER'S VIEW
                            // hasCompletedOnboarding = true
                            // forceMainApp = true
                            #endif
                        }
                }
            } else {
                // Add debug logging to confirm we're using the main TabView
                let _ = print("✅ MAIN APP: Showing main TabView with Finds tab")
                
                TabView(selection: $selectedTab) {
                        ScanTab()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Scan", systemImage: "camera")
                            }
                            .tag(0)
                        
                        NavigationView {
                            FindsView()
                        }
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Finds", systemImage: "list.bullet")
                            }
                            .tag(1)
                            .onAppear {
                                print("🎯 FINDS TAB: Selected and appeared, selectedTab = \(selectedTab)")
                            }
                        
                        ClosetListView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Closet", systemImage: "tshirt")
                            }
                            .tag(2)
                        
                        UserMeasurementProfileView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Fit", systemImage: "ruler")
                            }
                            .tag(3)
                        
                        MoreView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("More", systemImage: "ellipsis")
                            }
                            .tag(4)
                    }
                    .onChange(of: selectedTab) { oldValue, newValue in
                        print("🔄 TAB CHANGE: From \(oldValue) to \(newValue)")
                        print("🔄 TAB NAMES: 0=Scan, 1=Finds, 2=Closet, 3=Fit, 4=More")
                    }
                }
            }
        }
    }

