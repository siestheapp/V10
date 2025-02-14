import SwiftUI

struct HomeView: View {
    @State private var showUserStart = false
    
    var body: some View {
        if showUserStart {
            UserStart()
        } else {
            VStack {
                Text("sies")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemBackground))
            .onAppear {
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
                    withAnimation {
                        showUserStart = true
                    }
                }
            }
        }
    }
}

#Preview {
    HomeView()
}
