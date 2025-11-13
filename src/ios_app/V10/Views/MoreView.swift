import SwiftUI

struct MoreView: View {
    @EnvironmentObject var userSettings: UserSettings
    
    var body: some View {
        NavigationView {
            List {
                NavigationLink(destination: ShopView()) {
                    Label("Shop", systemImage: "bag")
                }
                NavigationLink(destination: CanvasView()) {
                    Label("Canvas", systemImage: "cpu")
                }
                NavigationLink(destination: ChatView()) {
                    Label("Ask AI", systemImage: "bubble.left.and.bubble.right.fill")
                }
                NavigationLink(destination: AccountScreen()) {
                    Label("Account", systemImage: "person")
                }
                NavigationLink(destination: BodyScreen()) {
                    Label("Body", systemImage: "figure.stand")
                }
            }
            .navigationTitle("More")
        }
    }
}

struct MoreView_Previews: PreviewProvider {
    static var previews: some View {
        MoreView()
            .environmentObject(UserSettings())
    }
} 