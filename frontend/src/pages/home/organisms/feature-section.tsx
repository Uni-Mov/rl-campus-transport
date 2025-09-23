import { useFeatures } from "../hooks/useFeatures";
export default function FeatureSection(){
  const features = useFeatures();
  return (
    <section id="features" className="pt-20 pb-40 px-4 bg-gray-50 scroll-mt-24">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">Features</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Built with cutting-edge technology to optimize campus transportation
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {features.map((feature, index) => (
          <div key={index} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow">
            <div className={`w-12 h-12 ${feature.wrap_icon} rounded-lg flex items-center justify-center mb-4`}>
               {feature.icon}
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </div>
        ))}
       </div>
      </div>
    </section>
  )
}