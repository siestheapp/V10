import SwiftUI

// @main  // TEMPORARILY DISABLED - Using original SiesApp
struct OptimizedSiesApp: App {
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
                // OPTIMIZED: All tabs are shown but data loading is deferred
                // Each view loads its data in onAppear, not at initialization
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
                }
            }
        }
    }
}
