import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Info, AlertCircle, X } from 'lucide-react';
import { useApp } from '../context/AppContext';
import './Notifications.css';

const Notifications = () => {
  const { state, dispatch, ActionTypes } = useApp();

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={18} />;
      case 'error':
        return <AlertCircle size={18} />;
      case 'info':
      default:
        return <Info size={18} />;
    }
  };

  return (
    <div className="notifications-container">
      <AnimatePresence>
        {(state.notifications || []).map((notification) => (
          <motion.div
            key={notification.id}
            className={`notification notification-${notification.type || 'info'}`}
            initial={{ opacity: 0, x: 100, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.8 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            <div className="notification-icon">
              {getIcon(notification.type)}
            </div>
            <div className="notification-content">
              <p>{notification.message}</p>
            </div>
            <button
              className="notification-close"
              onClick={() => dispatch({ 
                type: ActionTypes.REMOVE_NOTIFICATION, 
                payload: notification.id 
              })}
            >
              <X size={14} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default Notifications;
