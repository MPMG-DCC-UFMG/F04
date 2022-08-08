import React from "react";
import { Router, Redirect } from "@reach/router";
import routes from "./routes";
import Home from "./components/Home";
import Detail from "./components/Home/Detail";
import Login from "./components/Login";
import ProtectedRoute from "./components/ProtectedRoute";
import { logout } from "./services/auth";

function App() {
  return (
    <React.Fragment>
      <Router>
        <Login path={routes.login} />
        <ProtectedRoute component={Home} path={routes.home} />
        <ProtectedRoute component={Detail} path={routes.tweetDetail} />
        <ProtectedRoute
          component={() => {
            logout();

            return <Redirect to="/" noThrow />;
          }}
          path={routes.logout}
        />
        <ProtectedRoute
          component={() => {
            logout();

            return <Redirect to={`${routes.login}/0`} noThrow />;
          }}
          path="/"
        />
      </Router>
    </React.Fragment>
  );
}

export default App;
