export default function LoginFooter() {
  return (
    <div className="text-center mt-6">
      <p className="text-sm text-gray-600">
        {"Don't have an account? "}
        <a 
          href="/register" 
          className="text-emerald-500 hover:text-emerald-600 font-medium transition-colors"
        >
          Sign up
        </a>
      </p>
    </div>
  );
}
