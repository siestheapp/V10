import SwiftUI

struct HomeView: View {
    var body: some View {
        TabView {
            ClosetListView()
                .tabItem {
                    Label("Closet", systemImage: "tshirt")
                }
            
            BrandsView()
                .tabItem {
                    Label("Brands", systemImage: "tag")
                }
            
            AccountScreen()
                .tabItem {
                    Label("Account", systemImage: "person.circle")
                }
        }
    }
}

#Preview {
    HomeView()
}
