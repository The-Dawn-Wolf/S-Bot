import React, { useState } from 'react';

const Dashboard = ({ user, onLogout, history, onSave }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('plot');
    const [bookTitle, setBookTitle] = useState('');

    const handleFileUpload = async (e) => {
        if (!bookTitle) return alert("Please enter a title first!");
        setLoading(true);
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            setData(result);
            // Auto-save to Supabase via the prop from App.js
            onSave(result.analysis, result.metadata, bookTitle);
        } catch (err) {
            alert("Server Error. Ensure Python backend is running.");
        }
        setLoading(false);
    };

    return (
        <div className="flex min-h-screen bg-slate-50">
            {/* SIDEBAR: THE VAULT */}
            <aside className="w-80 bg-white border-r border-slate-200 p-6 hidden md:block">
                <h2 className="text-cyan-600 font-bold text-xl mb-6">Library Vault</h2>
                <div className="space-y-3">
                    {history.map((item) => (
                        <div key={item.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 cursor-pointer hover:border-cyan-300 transition-all">
                            <p className="font-bold text-slate-700 text-sm truncate">{item.book_title}</p>
                            <p className="text-xs text-slate-400">{item.genre}</p>
                        </div>
                    ))}
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="flex-1 p-10">
                <header className="flex justify-between mb-10">
                    <input 
                        type="text" placeholder="Project Name..." 
                        className="bg-transparent border-b-2 border-cyan-200 text-2xl outline-none focus:border-cyan-500 pb-2"
                        onChange={(e) => setBookTitle(e.target.value)}
                    />
                    <div className="flex gap-4">
                        <label className="bg-cyan-500 text-white px-6 py-3 rounded-xl font-bold cursor-pointer hover:shadow-lg transition-all">
                            + Analyze Manuscript
                            <input type="file" className="hidden" onChange={handleFileUpload} />
                        </label>
                        <button onClick={onLogout} className="text-slate-400 hover:text-red-500">Logout</button>
                    </div>
                </header>

                {loading ? (
                    <div className="flex flex-col items-center justify-center h-96">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-cyan-500 mb-4"></div>
                        <p className="text-cyan-600 font-medium">Neural Scanning in Progress...</p>
                    </div>
                ) : data ? (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in duration-500">
                        {/* LEFT: METADATA */}
                        <div className="space-y-6">
                            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                                <h3 className="text-slate-400 uppercase text-xs font-bold tracking-widest mb-4">Literary DNA</h3>
                                <div className="space-y-4">
                                    <StatRow label="Vocabulary" value={data.analysis.vocab_level} />
                                    <StatRow label="Word Count" value={data.metadata.word_count} />
                                    <StatRow label="Read Time" value={`${data.metadata.read_time}m`} />
                                    <StatRow label="Novel Type" value={data.analysis.novel_type} />
                                </div>
                            </div>
                        </div>

                        {/* RIGHT: SUMMARY TABS */}
                        <div className="lg:col-span-2 bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
                            <div className="flex bg-slate-50">
                                {['plot', 'thematic', 'emotional'].map(t => (
                                    <button 
                                        key={t} onClick={() => setActiveTab(t)}
                                        className={`flex-1 py-5 font-bold uppercase text-xs tracking-widest transition-all ${activeTab === t ? 'bg-white text-cyan-600 border-t-4 border-cyan-500' : 'text-slate-400'}`}
                                    >
                                        {t} summary
                                    </button>
                                ))}
                            </div>
                            <div className="p-10 leading-relaxed text-slate-600 text-lg">
                                {data.analysis.summaries[activeTab]}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="h-96 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-3xl">
                        <p className="text-slate-300">Enter a title and upload a text file to begin.</p>
                    </div>
                )}
            </main>
        </div>
    );
};

const StatRow = ({ label, value }) => (
    <div className="flex justify-between items-center py-2 border-b border-slate-50">
        <span className="text-slate-400 text-sm">{label}</span>
        <span className="font-bold text-slate-700">{value}</span>
    </div>
);

export default Dashboard;