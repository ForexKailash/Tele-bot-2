# database.py
import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.user_data = {}
        self.vip_users = {}
        self.free_signal_count = {}
        self.active_trades = {}
        self.load_all()
    
    def load_all(self):
        """Load all data from files"""
        try:
            with open('user_data.json', 'r') as f:
                self.user_data = json.load(f)
        except:
            pass
        
        try:
            with open('vip_users.json', 'r') as f:
                self.vip_users = json.load(f)
        except:
            pass
        
        try:
            with open('free_count.json', 'r') as f:
                self.free_signal_count = json.load(f)
        except:
            pass
        
        try:
            with open('active_trades.json', 'r') as f:
                self.active_trades = json.load(f)
        except:
            pass
    
    def save_all(self):
        """Save all data to files"""
        with open('user_data.json', 'w') as f:
            json.dump(self.user_data, f)
        
        with open('vip_users.json', 'w') as f:
            json.dump(self.vip_users, f)
        
        with open('free_count.json', 'w') as f:
            json.dump(self.free_signal_count, f)
        
        with open('active_trades.json', 'w') as f:
            json.dump(self.active_trades, f)
    
    def add_user(self, user_id, name, username):
        """Add new user"""
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {
                'name': name,
                'username': username,
                'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'active'
            }
            self.free_signal_count[str(user_id)] = 0
            self.save_all()
            return True
        return False
    
    def is_vip(self, user_id):
        """Check if user is VIP"""
        return str(user_id) in self.vip_users
    
    def add_vip(self, user_id, plan='Monthly'):
        """Add VIP user"""
        self.vip_users[str(user_id)] = {
            'plan': plan,
            'activated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_all()
    
    def get_free_count(self, user_id):
        """Get free signal count for user"""
        return self.free_signal_count.get(str(user_id), 0)
    
    def increment_free_count(self, user_id):
        """Increment free signal count"""
        uid = str(user_id)
        self.free_signal_count[uid] = self.free_signal_count.get(uid, 0) + 1
        self.save_all()
        return self.free_signal_count[uid]
    
    def reset_free_count(self, user_id):
        """Reset free signal count"""
        self.free_signal_count[str(user_id)] = 0
        self.save_all()
    
    def add_active_trade(self, trade_id, signal, message_id, channel_type):
        """Add active trade for tracking"""
        self.active_trades[trade_id] = {
            'signal': signal,
            'message_id': message_id,
            'channel_type': channel_type,
            'entry_time': datetime.now().isoformat(),
            'status': 'active'
        }
        self.save_all()
    
    def get_active_trades(self):
        """Get all active trades"""
        return self.active_trades
    
    def close_trade(self, trade_id, result):
        """Close a trade"""
        if trade_id in self.active_trades:
            self.active_trades[trade_id]['status'] = result
            self.active_trades[trade_id]['closed_time'] = datetime.now().isoformat()
            self.save_all()
            return self.active_trades[trade_id]
        return None
