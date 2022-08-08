import React, { useContext, useCallback } from "react";
import CustomToastContainer from "./CustomToastContainer";
import { toast } from "react-toastify";

const ToastContext = React.createContext(null);

const ToastProvider = ({ children }) => {
  const showSuccessMessage = useCallback((content) => {
    toast.success(content);
  }, []);

  const showErrorMessage = useCallback((content) => {
    toast.error(content);
  }, []);

  const showWarningMessage = useCallback((content) => {
    toast.warn(content);
  }, []);

  return (
    <ToastContext.Provider
      value={{
        showSuccessMessage,
        showErrorMessage,
        showWarningMessage,
      }}
    >
      <CustomToastContainer />
      {children}
    </ToastContext.Provider>
  );
};

const useToast = () => {
  const toastHelpers = useContext(ToastContext);

  return toastHelpers;
};

export { ToastContext, useToast };
export default ToastProvider;
