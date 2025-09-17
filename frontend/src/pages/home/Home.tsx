import {FeatureSection} from "./organisms/feature-section"
export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <FeatureSection />
      {/* Community Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">Join Our Community</h2>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Be part of the innovation happening at UNRC. Contribute to the future of campus transportation.
          </p>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="text-4xl font-bold text-emerald-600 mb-2">500+</div>
              <div className="text-gray-600">Expected daily users</div>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="text-4xl font-bold text-blue-600 mb-2">15min</div>
              <div className="text-gray-600">Average wait time reduction</div>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="text-4xl font-bold text-green-600 mb-2">100%</div>
              <div className="text-gray-600">Free for all users</div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-3 bg-emerald-600 text-white rounded-lg text-lg font-medium hover:bg-emerald-700 transition-colors">
              Get Early Access
            </button>     {/* this button redirect to register */}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <span className="font-bold text-gray-900">CampusTransport UNRC 2025</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <span>Built with ❤️ by UNRC students</span>
              <a href="#" className="hover:text-gray-900 transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-gray-900 transition-colors">
                Terms
              </a>
              <a href="#" className="hover:text-gray-900 transition-colors">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}