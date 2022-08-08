import { Grid, Header, Image, Button } from "semantic-ui-react";
import { useEffect, useState } from "react";
import LogoMP from "../../assets/logomp.png";
import api from "../../services/api";
import { login } from "../../services/auth";
import { useToast } from "../UI/Toast";
import routes from "../../routes";
import { useLocation } from "@reach/router";
export const Login = ({ navigate, token }) => {
  const { showSuccessMessage, showErrorMessage } = useToast();
  const { loading, setLoading } = useState(true);
  const location = useLocation();

  useEffect(() => {
    if (location.search.indexOf("noactivity") > -1) {
      showErrorMessage(
        "Você foi deslogado(a) por inatividade! Faça o Login novamente."
      );
    }
    if (token.length > 32)
      setTimeout(() => {
        api
          .get(`/logintoken?tk=${token}`)
          .then((response) => {
            login(response.data.access_token);
            showSuccessMessage("Seja bem-vindo(a)!");
            navigate(routes.home);
          })
          .catch((err) => {
            if (err.code === "ERR_NETWORK")
              showErrorMessage("Erro na conexão com o servidor!");
            else showErrorMessage("Login ou Senha estão incorretos!");
          });
      }, 1000);
  }, []);

  return (
    <Grid textAlign="center" style={{ height: "100vh" }} verticalAlign="middle">
      <Grid.Column style={{ maxWidth: 450 }}>
        <Header as="h2" color="red" textAlign="center">
          <Image src={LogoMP} /> F04 - ÁREA RESTRITA
        </Header>
        {token.length > 32 && <h3>Aguarde... estamos redirecionando você.</h3>}
        {token.length <= 32 && (
          <Button
            type="submit"
            color="red"
            fluid
            size="large"
            onClick={() =>
              (window.location = `${api.defaults.baseURL}authws02`)
            }
          >
            Entrar
          </Button>
        )}
      </Grid.Column>
    </Grid>
  );
};
