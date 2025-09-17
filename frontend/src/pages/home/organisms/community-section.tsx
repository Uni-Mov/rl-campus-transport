export default function CommunitySection() {
    return (  <section id="community" className="pt-4 md:pt-8 pb-20 px-4 bg-gray-50 scroll-mt-40">
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
      </section>)
}