
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';

const AGENT_STEPS = [
  { id: "logger", name: "Logger Agent", icon: "📝", description: "Preparing and logging case data.", duration: 1500 },
  { id: "investigator", name: "Investigation Agent", icon: "🔍", description: "Performing eligibility & validation checks.", duration: 2000 },
  { id: "actioning", name: "Actioning Agent", icon: "⚙️", description: "Processing data and making decisions.", duration: 2500 },
  { id: "verifier", name: "Verifier Agent", icon: "✅", description: "Running final validation checks.", duration: 1800 },
  { id: "communications", name: "Communications Agent", icon: "📧", description: "Generating notifications and advisories.", duration: 1500 },
];

type AgentStatus = 'pending' | 'processing' | 'completed';

const Simulation: React.FC = () => {
    const [searchParams] = useSearchParams();
    const runId = searchParams.get('run_id');
    const caseId = searchParams.get('case_id');
    const navigate = useNavigate();

    const [currentStep, setCurrentStep] = useState(0);
    const [statuses, setStatuses] = useState<AgentStatus[]>(AGENT_STEPS.map(() => 'pending'));
    const [isComplete, setIsComplete] = useState(false);
    
    useEffect(() => {
        if (!runId) {
            navigate('/');
            return;
        }

        const processNextStep = (stepIndex: number) => {
            if (stepIndex >= AGENT_STEPS.length) {
                setIsComplete(true);
                return;
            }

            // Set current step to 'processing'
            setStatuses(prev => {
                const newStatuses = [...prev];
                newStatuses[stepIndex] = 'processing';
                return newStatuses;
            });

            const agent = AGENT_STEPS[stepIndex];
            setTimeout(() => {
                // Set current step to 'completed'
                setStatuses(prev => {
                    const newStatuses = [...prev];
                    newStatuses[stepIndex] = 'completed';
                    return newStatuses;
                });
                setCurrentStep(stepIndex + 1);
                processNextStep(stepIndex + 1);
            }, agent.duration);
        };

        processNextStep(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [runId, navigate]);

    const overallProgress = (currentStep / AGENT_STEPS.length) * 100;
    
    const StatusBadge: React.FC<{ status: AgentStatus }> = ({ status }) => {
        const styles = {
            pending: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
            processing: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300 animate-pulse',
            completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        };
        return <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${styles[status]}`}>{status}</span>
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-6 md:p-8">
                <div className="text-center mb-8">
                    <h1 className="text-2xl md:text-3xl font-bold">Processing Simulation</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-2">Case ID: {caseId || 'N/A'}</p>
                </div>

                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-8">
                    <div className="bg-gradient-to-r from-yellow-400 to-amber-500 h-4 rounded-full transition-all duration-500" style={{ width: `${overallProgress}%` }}></div>
                </div>

                <div className="space-y-6">
                    {AGENT_STEPS.map((agent, index) => (
                        <div key={agent.id} className={`p-4 rounded-lg border-l-4 transition-all ${statuses[index] === 'processing' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' : statuses[index] === 'completed' ? 'border-green-500' : 'border-gray-300 dark:border-gray-600'}`}>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="text-2xl">{agent.icon}</div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">{agent.description}</p>
                                    </div>
                                </div>
                                <StatusBadge status={statuses[index]} />
                            </div>
                        </div>
                    ))}
                </div>

                {isComplete && (
                    <div className="mt-8 text-center p-6 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <h2 className="text-xl font-semibold text-green-700 dark:text-green-300">Processing Complete!</h2>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">The investigation workflow has finished successfully.</p>
                        <div className="mt-6 flex justify-center gap-4">
                            <Link to="/" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-gray-700 bg-gray-200 hover:bg-gray-300 dark:text-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600">
                                Back to Dashboard
                            </Link>
                             <Link to={`/report/${runId}`} className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-black bg-yellow-500 hover:bg-yellow-600">
                                View Full Report
                            </Link>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Simulation;
