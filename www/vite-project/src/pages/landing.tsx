import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/Navbar";
import { 
    Shield, 
    Zap, 
    LineChart, 
    Users, 
    Bell, 
    Lock, 
    BarChart2, 
    Brain,
    Search,
    Settings,
    AlertTriangle,
    FileText,
    Code,
    Terminal,
    ShieldCheck,
    Cpu,
    CheckCircle
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

// Enhanced attack prevention visualization
const AttackPreventionAnimation = () => {
    return (
        <div className="relative w-full h-[400px] bg-gradient-to-br from-white/15 via-blue-500/10 to-transparent backdrop-blur-lg rounded-2xl border border-white/30 overflow-hidden shadow-[0_0_60px_rgba(59,130,246,0.15)]">
            {/* Background effects */}
            <div className="absolute inset-0">
                <div className="absolute top-0 left-0 w-2/3 h-2/3 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full blur-3xl" />
                <div className="absolute bottom-0 right-0 w-2/3 h-2/3 bg-gradient-to-tl from-blue-600/20 to-transparent rounded-full blur-3xl" />
            </div>

            <AnimatePresence>
                {/* Animated attacks */}
                {[
                    { 
                        icon: <Code />,
                        text: "SELECT * FROM users WHERE id = 1 OR 1=1;",
                        position: "top-1/4",
                        delay: 0 
                    },
                    { 
                        icon: <Terminal />,
                        text: "../../../etc/passwd",
                        position: "top-2/4",
                        delay: 2 
                    },
                    { 
                        icon: <AlertTriangle />,
                        text: "<script>alert('XSS')</script>",
                        position: "top-3/4",
                        delay: 4 
                    }
                ].map((attack, index) => (
                    <motion.div
                        key={index}
                        initial={{ x: "-100%", opacity: 0 }}
                        animate={{ 
                            x: ["0%", "100%"],
                            opacity: [0, 1, 1, 0]
                        }}
                        exit={{ x: "100%", opacity: 0 }}
                        transition={{ 
                            duration: 3,
                            repeat: Infinity,
                            repeatDelay: 3,
                            delay: attack.delay
                        }}
                        className={cn(
                            "absolute flex items-center gap-3 bg-gradient-to-r from-red-500/40 to-red-500/20 backdrop-blur-sm px-6 py-3 rounded-xl border border-red-500/40",
                            attack.position,
                            "left-0 shadow-[0_0_40px_rgba(239,68,68,0.3)]"
                        )}
                    >
                        <div className="text-red-300 drop-shadow-[0_0_15px_rgba(239,68,68,0.6)]">
                            {attack.icon}
                        </div>
                        <span className="text-red-200 font-mono text-sm whitespace-nowrap font-semibold drop-shadow-[0_0_15px_rgba(239,68,68,0.6)]">
                            {attack.text}
                        </span>
                    </motion.div>
                ))}

                {/* Shield Animation */}
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                    <motion.div
                        className="relative"
                        animate={{
                            scale: [1, 1.1, 1],
                            rotate: [0, -5, 5, 0],
                        }}
                        transition={{
                            duration: 4,
                            repeat: Infinity,
                            repeatType: "reverse",
                        }}
                    >
                        {/* Glowing background */}
                        <motion.div
                            className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500/40 to-blue-600/40 blur-2xl"
                            animate={{
                                scale: [1, 1.5, 1],
                                opacity: [0.4, 0.7, 0.4]
                            }}
                            transition={{
                                duration: 4,
                                repeat: Infinity,
                                repeatType: "reverse"
                            }}
                        />
                        
                        {/* Shield icon */}
                        <ShieldCheck className="w-32 h-32 text-blue-300 relative z-10 drop-shadow-[0_0_40px_rgba(96,165,250,0.6)]" />
                        
                        {/* Rotating circles */}
                        <motion.div
                            className="absolute inset-0 border-4 border-blue-400/50 rounded-full shadow-[0_0_40px_rgba(96,165,250,0.4)]"
                            animate={{ rotate: 360 }}
                            transition={{
                                duration: 8,
                                repeat: Infinity,
                                ease: "linear"
                            }}
                        />
                        <motion.div
                            className="absolute inset-4 border-4 border-blue-400/40 rounded-full shadow-[0_0_40px_rgba(96,165,250,0.3)]"
                            animate={{ rotate: -360 }}
                            transition={{
                                duration: 12,
                                repeat: Infinity,
                                ease: "linear"
                            }}
                        />
                    </motion.div>
                </div>

                {/* Success Messages */}
                <div className="absolute bottom-6 left-0 w-full flex justify-center gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1 }}
                        className="flex items-center gap-3 bg-gradient-to-r from-green-500/40 to-green-500/20 backdrop-blur-sm px-6 py-3 rounded-xl border border-green-500/40 shadow-[0_0_40px_rgba(34,197,94,0.3)]"
                    >
                        <CheckCircle className="text-green-300 drop-shadow-[0_0_15px_rgba(34,197,94,0.6)]" />
                        <span className="text-green-200 font-semibold drop-shadow-[0_0_15px_rgba(34,197,94,0.6)]">Threats Blocked</span>
                    </motion.div>
                    
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1.5 }}
                        className="flex items-center gap-3 bg-gradient-to-r from-blue-500/40 to-blue-500/20 backdrop-blur-sm px-6 py-3 rounded-xl border border-blue-500/40 shadow-[0_0_40px_rgba(96,165,250,0.3)]"
                    >
                        <Brain className="text-blue-300 drop-shadow-[0_0_15px_rgba(96,165,250,0.6)]" />
                        <span className="text-blue-200 font-semibold drop-shadow-[0_0_15px_rgba(96,165,250,0.6)]">ML Analysis Active</span>
                    </motion.div>
                </div>
            </AnimatePresence>
        </div>
    );
};

export function LandingPage() {
    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-b from-blue-600 to-blue-800">
            <div className="absolute inset-0 bg-[url('/assets/images/auth-bg-pattern.svg')] bg-repeat [mask-image:linear-gradient(to_bottom,white,transparent)]" />
            <div className="relative">
                <Navbar variant="light" />
                
                {/* Hero Section */}
                <section className="relative flex-1 flex items-center justify-center py-20 overflow-hidden">
                    <div className="container px-4 md:px-6 relative">
                        <div className="flex flex-col lg:flex-row items-center gap-12">
                            <div className="flex-1 space-y-8 text-center lg:text-left">
                                <div className="space-y-4">
                                    <motion.h1 
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.5 }}
                                        className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl"
                                    >
                                        <span className="text-white drop-shadow-[0_0_35px_rgba(255,255,255,0.6)] bg-gradient-to-r from-white to-blue-100 bg-clip-text">
                                            AI-Powered Security with
                                        </span>
                                        <span className="block text-blue-200 drop-shadow-[0_0_35px_rgba(191,219,254,0.6)] bg-gradient-to-r from-blue-200 to-white bg-clip-text">
                                            VESSA
                                        </span>
                                    </motion.h1>
                                    <motion.p 
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.5, delay: 0.2 }}
                                        className="mx-auto lg:mx-0 max-w-[700px] text-white/95 md:text-xl font-medium drop-shadow-[0_0_30px_rgba(255,255,255,0.5)] bg-gradient-to-r from-white to-blue-100 bg-clip-text"
                                    >
                                        Heuristic firewall with ML-driven threat detection and automated incident response.
                                        Built for modern enterprises, powered by advanced AI.
                                    </motion.p>
                                </div>
                                <motion.div 
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.5, delay: 0.4 }}
                                    className="space-x-4"
                                >
                                    <Link to="/signup">
                                        <Button size="lg" className="h-12 px-8 bg-white text-blue-600 hover:bg-blue-50 shadow-[0_0_30px_rgba(255,255,255,0.2)]">
                                            Start Free Trial
                                        </Button>
                                    </Link>
                                    <Link to="/demo">
                                        <Button variant="outline" size="lg" className="h-12 px-8 bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                                            Request Demo
                                        </Button>
                                    </Link>
                                </motion.div>
                            </div>
                            
                            {/* Hero Animation */}
                            <motion.div 
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ duration: 0.5, delay: 0.6 }}
                                className="flex-1 relative z-10"
                            >
                                <div className="relative">
                                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/30 to-white/10 rounded-2xl blur-3xl" />
                                    <div className="relative backdrop-blur-sm rounded-2xl p-8">
                                        <AttackPreventionAnimation />
                                        <div className="mt-6 grid grid-cols-2 gap-6">
                                            <div className="bg-gradient-to-br from-white/20 to-white/10 backdrop-blur-sm p-5 rounded-xl border border-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                                                <Terminal className="w-7 h-7 text-blue-200 mb-3 drop-shadow-[0_0_10px_rgba(96,165,250,0.5)]" />
                                                <p className="text-sm text-white font-semibold drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">Real-time Detection</p>
                                            </div>
                                            <div className="bg-gradient-to-br from-white/20 to-white/10 backdrop-blur-sm p-5 rounded-xl border border-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                                                <Brain className="w-7 h-7 text-blue-200 mb-3 drop-shadow-[0_0_10px_rgba(96,165,250,0.5)]" />
                                                <p className="text-sm text-white font-semibold drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">ML Analysis</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    </div>
                </section>

                {/* Core Features Section */}
                <section className="py-20 relative flex items-center justify-center">
                    <div className="container px-4 md:px-6 relative">
                        <motion.h2 
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="text-3xl font-bold text-center mb-12 text-white"
                        >
                            AI-Powered Security Features
                        </motion.h2>
                        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
                            {[
                                {
                                    icon: <Shield className="h-6 w-6 text-blue-300" />,
                                    title: "Heuristic Protection",
                                    description: "ML-powered threat detection with real-time pattern analysis"
                                },
                                {
                                    icon: <Brain className="h-6 w-6 text-blue-300" />,
                                    title: "Multi-Classification",
                                    description: "Advanced AI models for precise threat classification"
                                },
                                {
                                    icon: <Cpu className="h-6 w-6 text-blue-300" />,
                                    title: "Automated Response",
                                    description: "Intelligent response workflows with ML-driven decisions"
                                },
                                {
                                    icon: <LineChart className="h-6 w-6 text-blue-300" />,
                                    title: "Predictive Analytics",
                                    description: "AI-driven threat prediction and proactive security"
                                }
                            ].map((feature, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: index * 0.1 }}
                                    className="group relative"
                                >
                                    <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-white/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <div className="relative p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-colors">
                                        <div className="p-3 bg-white/5 rounded-xl w-fit">
                                            {feature.icon}
                                        </div>
                                        <h3 className="text-xl font-semibold mt-4 text-white">{feature.title}</h3>
                                        <p className="mt-2 text-blue-100">{feature.description}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Services Section */}
                <section className="py-20 relative bg-gradient-to-b from-blue-600 to-blue-800 flex items-center justify-center">
                    <div className="container px-4 md:px-6 relative">
                        <motion.h2 
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="text-3xl font-bold text-center mb-12 text-white"
                        >
                            Advanced Security Services
                        </motion.h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <motion.div 
                                initial={{ opacity: 0, x: -20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                className="relative group"
                            >
                                <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-white/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                                <div className="relative p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-colors">
                                    <h3 className="text-2xl font-semibold mb-6 text-white flex items-center gap-3">
                                        <AlertTriangle className="h-6 w-6 text-blue-300" />
                                        Threat Prevention
                                    </h3>
                                    <div className="space-y-4">
                                        {[
                                            { icon: <Code className="h-4 w-4" />, text: "SQL Injection Detection" },
                                            { icon: <Terminal className="h-4 w-4" />, text: "XSS Attack Mitigation" },
                                            { icon: <Shield className="h-4 w-4" />, text: "Command Injection Protection" },
                                            { icon: <Lock className="h-4 w-4" />, text: "Path Traversal Defense" }
                                        ].map((item, index) => (
                                            <div key={index} className="flex items-center gap-3 text-blue-100">
                                                <div className="p-2 bg-white/5 rounded-lg">
                                                    {item.icon}
                                                </div>
                                                <span>{item.text}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </motion.div>
                            <motion.div 
                                initial={{ opacity: 0, x: 20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                className="relative group"
                            >
                                <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-white/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                                <div className="relative p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-colors">
                                    <h3 className="text-2xl font-semibold mb-6 text-white flex items-center gap-3">
                                        <Brain className="h-6 w-6 text-blue-300" />
                                        AI Capabilities
                                    </h3>
                                    <div className="space-y-4">
                                        {[
                                            { icon: <Cpu className="h-4 w-4" />, text: "Multi-Classification Models" },
                                            { icon: <BarChart2 className="h-4 w-4" />, text: "Pattern Recognition" },
                                            { icon: <LineChart className="h-4 w-4" />, text: "Anomaly Detection" },
                                            { icon: <Zap className="h-4 w-4" />, text: "Real-time Learning" }
                                        ].map((item, index) => (
                                            <div key={index} className="flex items-center gap-3 text-blue-100">
                                                <div className="p-2 bg-white/5 rounded-lg">
                                                    {item.icon}
                                                </div>
                                                <span>{item.text}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    </div>
                </section>

                {/* Statistics Section */}
                <section className="py-20 relative flex items-center justify-center">
                    <div className="container px-4 md:px-6 relative">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                            {[
                                { value: "99.9%", label: "Threat Detection" },
                                { value: "24/7", label: "AI Monitoring" },
                                { value: "500+", label: "Enterprise Clients" },
                                { value: "<1min", label: "Response Time" }
                            ].map((stat, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: index * 0.1 }}
                                    className="relative group"
                                >
                                    <div className="absolute inset-0 bg-white/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <div className="relative p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-colors text-center">
                                        <h4 className="text-4xl font-bold text-white mb-2">{stat.value}</h4>
                                        <p className="text-blue-100">{stat.label}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* CTA Section */}
                <section className="py-20 relative flex items-center justify-center">
                    <div className="container px-4 md:px-6 relative">
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="relative group max-w-3xl mx-auto"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-white/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="relative p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 transition-colors text-center">
                                <h2 className="text-3xl font-bold text-white mb-4">
                                    Ready to Strengthen Your Security?
                                </h2>
                                <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
                                    Join industry leaders who trust VESSA's AI-powered security.
                                    Experience the future of threat detection today.
                                </p>
                                <div className="flex justify-center gap-4">
                                    <Link to="/signup">
                                        <Button size="lg" className="h-11 px-8 bg-white text-blue-600 hover:bg-blue-50">
                                            Start Free Trial
                                        </Button>
                                    </Link>
                                    <Link to="/contact">
                                    <Button variant="outline" size="lg" className="h-12 px-8 bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                                            Contact Sales
                                        </Button>
                                    </Link>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </section>
            </div>
        </div>
    );
} 