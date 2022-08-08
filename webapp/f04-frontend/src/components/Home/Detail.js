import React, { useEffect, useState } from "react";
import {
  Tab,
  Header,
  Icon,
  Button,
  Table,
  Image,
  Label,
  Grid,
} from "semantic-ui-react";
import { NavBar } from "../UI/NavBar";
import api from "../../services/api";
import { useToast } from "../UI/Toast";
import routes from "../../routes";
import Swal from "sweetalert2";
const Detail = ({ navigate, id }) => {
  const [tweet, setTweet] = useState({});
  const { showErrorMessage } = useToast();
  const getDetails = () => {
    api
      .get(`/tweets/${id}`)
      .then((response) => {
        setTweet(response.data.data);
      })
      .catch((err) => {
        showErrorMessage("Não foi possível buscar os dados.");
      });
  };

  useEffect(() => {
    getDetails();
  }, [setTweet]);

  const relabel = () => {
    Swal.fire({
      title: "Aviso!",
      text: "Você confirma que este post NÃO contém uma mensagem política de campanha antecipada?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "SIM",
      cancelButtonText: "NÃO",
    });
  };

  const panes = [
    {
      menuItem: "Sobre o Tweet",
      render: () => (
        <Tab.Pane>
          <Label as="a" color="red" ribbon>
            {tweet.score * 100}%
          </Label>
          <Table celled>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell textAlign="right">Atributo</Table.HeaderCell>
                <Table.HeaderCell>Valor</Table.HeaderCell>
              </Table.Row>
            </Table.Header>

            <Table.Body>
              <Table.Row>
                <Table.Cell textAlign="right">Texto</Table.Cell>

                <Table.Cell>{tweet.text}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Data da Postagem</Table.Cell>

                <Table.Cell>{tweet.created_at}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Hashtags</Table.Cell>

                <Table.Cell>
                  {tweet.entities?.hashtags?.map((t) => (
                    <a
                      href={`https://twitter.com/search?q=%23${t.tag}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {" - "}#{t.tag}{" "}
                    </a>
                  ))}
                </Table.Cell>
              </Table.Row>
              {tweet.media && (
                <Table.Row>
                  <Table.Cell textAlign="right">Imagens do tweet </Table.Cell>

                  <Table.Cell>
                    {tweet.media?.map((m) => (
                      <Image src={m.url} />
                    ))}
                  </Table.Cell>
                </Table.Row>
              )}
              <Table.Row>
                <Table.Cell textAlign="right">Comentários</Table.Cell>

                <Table.Cell>{tweet?.reply_count}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Retweets</Table.Cell>

                <Table.Cell>{tweet?.retweet_count}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Curtidas</Table.Cell>

                <Table.Cell>{tweet?.like_count}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Quotes</Table.Cell>

                <Table.Cell>{tweet?.quote_count}</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        </Tab.Pane>
      ),
    },

    {
      menuItem: "Sobre o Usuário",
      render: () => (
        <Tab.Pane>
          <Table celled>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell textAlign="right">Atributo</Table.HeaderCell>
                <Table.HeaderCell>Valor</Table.HeaderCell>
              </Table.Row>
            </Table.Header>

            <Table.Body>
              <Table.Row>
                <Table.Cell textAlign="right">
                  ID do usuário no Twitter
                </Table.Cell>

                <Table.Cell>{tweet.user.id}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Imagem de Perfil</Table.Cell>

                <Table.Cell>
                  <img
                    src={tweet.user?.profile_image_url}
                    alt="Imagem de Perfil do Usuário"
                  />
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Nome</Table.Cell>

                <Table.Cell>{tweet.user.name}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Nome de usuário</Table.Cell>

                <Table.Cell>
                  <Icon name="twitter" />
                  <a
                    href={`https://twitter.com/${tweet.user.username}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    @{tweet.user.username}
                  </a>
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Criado em</Table.Cell>

                <Table.Cell>{tweet.user.created_at}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Biografia</Table.Cell>

                <Table.Cell>{tweet.user.description}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Loalização</Table.Cell>

                <Table.Cell>{tweet.user?.location}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Site</Table.Cell>

                <Table.Cell>{tweet.user?.url}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell textAlign="right">Perfil Verificado</Table.Cell>

                <Table.Cell>{tweet.user?.verified ? "SIM" : "NÃO"}</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        </Tab.Pane>
      ),
    },
  ];

  return (
    <>
      <NavBar />
      <Header as="h2" size="large">
        <Icon name="twitter" />
        <Header.Content>
          {tweet.user?.name} - @{tweet.user?.username}
          <Header.Subheader> {tweet.text}</Header.Subheader>
        </Header.Content>
      </Header>

      <Grid fluid padded>
        <Grid.Column>
          <Button
            as="a"
            color="teal"
            position="left"
            onClick={() => navigate(routes.home)}
          >
            <Icon name="arrow left" />
            voltar
          </Button>
          <Button
            as="a"
            circular
            color="twitter"
            icon="twitter"
            target="_blank"
            href={`https://twitter.com/${tweet.user?.id}/status/${tweet.id}`}
          />
          <Button
            as="a"
            circular
            color="red"
            icon="thumbs down"
            onClick={() => {
              relabel();
            }}
          />

          <Button
            as="a"
            circular
            color="green"
            icon="thumbs up"
            onClick={() => {
              relabel();
            }}
          />
        </Grid.Column>
      </Grid>
      <Tab
        menu={{ fluid: true, vertical: false }}
        menuPosition="left"
        panes={panes}
      />
    </>
  );
};

export default Detail;
