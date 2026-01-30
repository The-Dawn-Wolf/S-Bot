import React, { useState } from 'react';

const Login = ({ onLogin }) => {
    const [email, setEmail] = useState('');

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
            <div className="bg-white p-10 rounded-3xl shadow-2xl border border-cyan-100 w-full max-w-md transform transition-all hover:scale-105">
                <div className="text-center mb-8">
                    <div className="bg-cyan-500 w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg shadow-cyan-200">
                        <span className="text-white text-2xl font-bold">S</span>
                    </div>
                    <h1 className="text-3xl font-extrabold text-slate-800">Shelfie Intelligence</h1>
                    <p className="text-slate-400">Enter the literary laboratory</p>
                </div>
                <div className="space-y-4">
                    <input 
                        type="email" placeholder="Email Address" 
                        className="w-full px-5 py-4 rounded-xl border border-slate-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 outline-none transition-all"
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <input 
                        type="password" placeholder="Access Key" 
                        className="w-full px-5 py-4 rounded-xl border border-slate-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 outline-none transition-all"
                    />
                    <button 
                        onClick={() => onLogin(email)}
                        className="w-full bg-cyan-500 text-white font-bold py-4 rounded-xl hover:bg-cyan-600 shadow-lg shadow-cyan-100 active:scale-95 transition-all"
                    >
                        UNSEAL THE VAULT
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;