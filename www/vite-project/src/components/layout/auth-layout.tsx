import { Link } from "react-router-dom";
import { Navbar } from "@/components/Navbar";

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle: string;
    altLink: {
        text: string;
        href: string;
        label: string;
    };
}

export function AuthLayout({ children, title, subtitle, altLink }: AuthLayoutProps) {
    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />
            <div className="container relative flex-1 flex items-center justify-center md:grid lg:max-w-none lg:px-0">
                <div className="lg:p-8">
                    <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
                        <div className="flex flex-col space-y-2 text-center">
                            <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
                            <p className="text-sm text-muted-foreground">{subtitle}</p>
                        </div>
                        {children}
                        <p className="px-8 text-center text-sm text-muted-foreground">
                            {altLink.text}{" "}
                            <Link 
                                to={altLink.href}
                                className="underline underline-offset-4 hover:text-primary"
                            >
                                {altLink.label}
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
} 