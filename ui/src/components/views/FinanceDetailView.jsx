import React, { useState } from 'react';
import { DollarSign, TrendingUp, TrendingDown, CreditCard, PiggyBank, Receipt, AlertTriangle, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import DetailViewLayout from '../DetailViewLayout';

const FinanceDetailView = () => {
    const [activeTab, setActiveTab] = useState('overview');

    const accounts = [
        { id: 1, name: 'Checking Account', balance: 8542.50, change: +245.00, type: 'checking' },
        { id: 2, name: 'Savings Account', balance: 24150.00, change: +150.00, type: 'savings' },
        { id: 3, name: 'Investment Portfolio', balance: 45230.00, change: +1250.00, changePercent: 2.8, type: 'investment' },
    ];

    const recentTransactions = [
        { id: 1, merchant: 'Amazon', amount: -89.99, category: 'Shopping', date: 'Today', icon: '📦' },
        { id: 2, merchant: 'Whole Foods', amount: -156.32, category: 'Groceries', date: 'Today', icon: '🛒' },
        { id: 3, merchant: 'Salary Deposit', amount: +5200.00, category: 'Income', date: 'Yesterday', icon: '💰' },
        { id: 4, merchant: 'Netflix', amount: -15.99, category: 'Entertainment', date: 'Yesterday', icon: '🎬' },
        { id: 5, merchant: 'Gas Station', amount: -45.00, category: 'Transportation', date: '2 days ago', icon: '⛽' },
    ];

    const upcomingBills = [
        { id: 1, name: 'Electric Bill', amount: 120.00, dueDate: 'Dec 15', status: 'upcoming' },
        { id: 2, name: 'Internet', amount: 79.99, dueDate: 'Dec 18', status: 'upcoming' },
        { id: 3, name: 'Car Insurance', amount: 185.00, dueDate: 'Dec 20', status: 'upcoming' },
    ];

    const budget = {
        total: 4000,
        spent: 2850,
        categories: [
            { name: 'Housing', allocated: 1500, spent: 1500, color: '#00d9ff' },
            { name: 'Food', allocated: 600, spent: 480, color: '#10b981' },
            { name: 'Transport', allocated: 400, spent: 320, color: '#f59e0b' },
            { name: 'Entertainment', allocated: 300, spent: 250, color: '#8b5cf6' },
            { name: 'Other', allocated: 200, spent: 300, color: '#ef4444' },
        ]
    };

    return (
        <DetailViewLayout title="Finance" icon={DollarSign} currentDomain="finance">
            <div className="finance-detail">
                {/* Stats Overview */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
                            <DollarSign size={24} className="text-green-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">$77,922</span>
                            <span className="stat-label">Total Balance</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(0, 217, 255, 0.1)' }}>
                            <TrendingUp size={24} className="text-cyan-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">+$1,645</span>
                            <span className="stat-label">This Month</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)' }}>
                            <Receipt size={24} className="text-yellow-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">$385</span>
                            <span className="stat-label">Bills Due</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.1)' }}>
                            <PiggyBank size={24} className="text-purple-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">71%</span>
                            <span className="stat-label">Budget Used</span>
                        </div>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="detail-tabs">
                    <button 
                        className={`detail-tab ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Accounts
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'transactions' ? 'active' : ''}`}
                        onClick={() => setActiveTab('transactions')}
                    >
                        Transactions
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'bills' ? 'active' : ''}`}
                        onClick={() => setActiveTab('bills')}
                    >
                        Bills
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'budget' ? 'active' : ''}`}
                        onClick={() => setActiveTab('budget')}
                    >
                        Budget
                    </button>
                </div>

                {/* Tab Content */}
                <div className="tab-content">
                    {activeTab === 'overview' && (
                        <div className="accounts-list">
                            {accounts.map((account) => (
                                <div key={account.id} className="account-card">
                                    <div className="account-icon">
                                        {account.type === 'checking' && <CreditCard size={24} />}
                                        {account.type === 'savings' && <PiggyBank size={24} />}
                                        {account.type === 'investment' && <TrendingUp size={24} />}
                                    </div>
                                    <div className="account-info">
                                        <span className="account-name">{account.name}</span>
                                        <span className="account-balance">
                                            ${account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                                        </span>
                                    </div>
                                    <div className={`account-change ${account.change >= 0 ? 'positive' : 'negative'}`}>
                                        {account.change >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                                        <span>${Math.abs(account.change).toFixed(2)}</span>
                                        {account.changePercent && <span className="change-percent">({account.changePercent}%)</span>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'transactions' && (
                        <div className="transactions-list">
                            {recentTransactions.map((tx) => (
                                <div key={tx.id} className="transaction-item">
                                    <span className="tx-icon">{tx.icon}</span>
                                    <div className="tx-info">
                                        <span className="tx-merchant">{tx.merchant}</span>
                                        <span className="tx-category">{tx.category}</span>
                                    </div>
                                    <div className="tx-details">
                                        <span className={`tx-amount ${tx.amount >= 0 ? 'positive' : 'negative'}`}>
                                            {tx.amount >= 0 ? '+' : ''}{tx.amount.toFixed(2)}
                                        </span>
                                        <span className="tx-date">{tx.date}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'bills' && (
                        <div className="bills-list">
                            {upcomingBills.map((bill) => (
                                <div key={bill.id} className="bill-item">
                                    <Receipt size={20} className="text-yellow-400" />
                                    <div className="bill-info">
                                        <span className="bill-name">{bill.name}</span>
                                        <span className="bill-due">Due: {bill.dueDate}</span>
                                    </div>
                                    <span className="bill-amount">${bill.amount.toFixed(2)}</span>
                                    <button className="btn-secondary">Pay Now</button>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'budget' && (
                        <div className="budget-overview">
                            <div className="budget-summary">
                                <div className="budget-total">
                                    <span className="budget-spent">${budget.spent}</span>
                                    <span className="budget-of">of ${budget.total}</span>
                                </div>
                                <div className="budget-bar">
                                    <div 
                                        className="budget-fill" 
                                        style={{ width: `${(budget.spent / budget.total) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                            <div className="budget-categories">
                                {budget.categories.map((cat, idx) => (
                                    <div key={idx} className="budget-category">
                                        <div className="cat-header">
                                            <span className="cat-color" style={{ background: cat.color }}></span>
                                            <span className="cat-name">{cat.name}</span>
                                            <span className="cat-amount">
                                                ${cat.spent} / ${cat.allocated}
                                            </span>
                                        </div>
                                        <div className="cat-bar">
                                            <div 
                                                className="cat-fill" 
                                                style={{ 
                                                    width: `${Math.min((cat.spent / cat.allocated) * 100, 100)}%`,
                                                    background: cat.spent > cat.allocated ? '#ef4444' : cat.color
                                                }}
                                            ></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </DetailViewLayout>
    );
};

export default FinanceDetailView;


