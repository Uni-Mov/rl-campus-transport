import LoginHeader from "./organisms/LoginHeader";
import LoginForm from "./organisms/LoginForm";
import LoginFooter from "./organisms/LoginFooter";

export default function Login() { 
  return (
      <main className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <LoginHeader />
          <LoginForm />
          <LoginFooter />
        </div>
      </main>
  )
}