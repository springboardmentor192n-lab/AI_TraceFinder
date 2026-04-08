import React from 'react';
import { Fingerprint, ScanLine, ShieldCheck, Cpu } from 'lucide-react';

const About = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 lg:p-10">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 md:p-12">

        <div className="text-center mb-10">
          <div className="inline-block bg-red-600/10 border border-red-500/20 p-4 rounded-full mb-6">
            <Fingerprint className="w-10 h-10 text-red-500" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">TraceFinder</h1>
          <p className="text-gray-400 max-w-xl mx-auto">Advanced Forensic Scanner Identification System</p>
        </div>

        <div className="space-y-8 text-gray-300">
          <div className="flex gap-4">
            <div className="p-3 bg-slate-800 rounded-lg h-fit"><ScanLine className="w-6 h-6 text-indigo-400" /></div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Scanner Fingerprinting</h3>
              <p className="text-sm text-gray-400 leading-relaxed">Analyzes unique noise patterns (PRNU) left by scanner sensors on digital documents to identify the source device.</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="p-3 bg-slate-800 rounded-lg h-fit"><Cpu className="w-6 h-6 text-emerald-400" /></div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Deep Learning Powered</h3>
              <p className="text-sm text-gray-400 leading-relaxed">Utilizes a custom-trained Deep Convolutional Neural Network (CNN) to classify over 44 different scanner models with high accuracy.</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="p-3 bg-slate-800 rounded-lg h-fit"><ShieldCheck className="w-6 h-6 text-purple-400" /></div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Digital Forensics</h3>
              <p className="text-sm text-gray-400 leading-relaxed">Designed for digital forensics, legal evidence verification, and copyright authentication tasks to detect tampering or fraudulent documents.</p>
            </div>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-slate-800 text-center">
          <p className="text-xs text-gray-500">Built with React, Tailwind CSS, PyTorch & Flask.</p>
        </div>
      </div>
    </div>
  );
};

export default About;