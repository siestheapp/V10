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
                            // For development, auto-complete onboarding
                            #if DEBUG
                            print("🚀 DEBUG: Setting hasCompletedOnboarding to true")
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                                hasCompletedOnboarding = true
                                forceMainApp = true
                            }
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
                        
                        ScanHistoryView()
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
                        
                        ShopView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("Shop", systemImage: "bag")
                            }
                            .tag(4)
                        
                        MoreView()
                            .environmentObject(userSettings)
                            .tabItem {
                                Label("More", systemImage: "ellipsis")
                            }
                            .tag(5)
                    }
                    .onChange(of: selectedTab) { oldValue, newValue in
                        print("🔄 TAB CHANGE: From \(oldValue) to \(newValue)")
                        print("🔄 TAB NAMES: 0=Scan, 1=Finds, 2=Closet, 3=Fit, 4=Shop, 5=More")
                    }
                }
            }
        }
    }

