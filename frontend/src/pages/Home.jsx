import { Link } from "react-router-dom";
import Button from "../components/Button.jsx";
import { APP_NAME } from "../utils/constants";

export default function Home() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center gap-5 px-4 py-14 text-center sm:gap-6 sm:px-6 sm:py-24">
      <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">{APP_NAME}</h1>
      <p className="text-base text-gray-600 sm:text-lg">
        Upload a screenplay and get an AI-generated production breakdown characters, props,
        locations, costumes, and departments in minutes instead of hours.
      </p>
      <div className="grid w-full gap-3 sm:flex sm:w-auto">
        <Link to="/register" className="w-full sm:w-auto">
          <Button className="w-full sm:w-auto">Get started</Button>
        </Link>
        <Link to="/login" className="w-full sm:w-auto">
          <Button variant="secondary" className="w-full sm:w-auto">Log in</Button>
        </Link>
      </div>
    </div>
  );
}
