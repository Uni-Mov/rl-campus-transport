import { Sparkles, CarFront, Zap } from 'lucide-react';

export function useFeatures() {
  const features = [
    {
      icon: <Sparkles color="green" size="24" />,
      wrap_icon: "bg-emerald-100",
      title: "AI Route Optimization",
      description:
        "Reinforcement Learning algorithms decide optimal passenger pickups based on location and route efficiency",
    },
    {
      icon: <CarFront color="blue" size="24" />,
      wrap_icon: "bg-blue-100",
      title: "Flexible Roles",
      description:
        "Any university member can register as driver or passenger, with the ability to switch roles anytime",
    },
    {
      icon: <Zap className="text-yellow-500" size="24" />,
      wrap_icon: "bg-yellow-100",
      title: "Completely Free",
      description:
        "No payments, no cost-sharing. A community-driven solution for campus transportation needs",
    },
  ];

  return features;
}


