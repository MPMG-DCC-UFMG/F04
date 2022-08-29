import React, { useState } from "react";
import {
  Header,
  Table,
  Button,
  Icon,
  Label,
  Grid,
  Message,
} from "semantic-ui-react";
import PropTypes from "prop-types";
import { useNavigate } from "@reach/router";
import eventBus from "../../services/eventBus";
import { format } from "date-fns";
const ListTable = ({ tweets, relabel, loading }) => {
  const navigate = useNavigate();

  const [sortState, setSortState] = useState({
    score: "down",
    retweets: "down",
  });

  const convertHashtags = (text) => {
    return text.replace(
      /(^|\s)(#[a-z0-9\d-]+)/gi,
      "$1<a href='https://twitter.com/search?q=$2' target='_blank'>$2</a>"
    );
  };

  const convertUsers = (text) => {
    return text.replace(
      /(^|\s)(@[a-z0-9\d-_]+)/gi,
      "$1<a href='https://twitter.com/$2' target='_blank'>$2</a>"
    );
  };

  const toogleSort = (attribute) => {
    setSortState({
      [attribute]: sortState[attribute] === "up" ? "down" : "up",
    });

    console.log(sortState);

    const filters = JSON.parse(localStorage.getItem("SEARCH_FILTERS"));
    localStorage.setItem(
      "SEARCH_FILTERS",
      JSON.stringify({
        ...filters,
        sortBy: sortState,
      })
    );

    eventBus.dispatch("tweetSortBy", sortState);
  };

  return (
    <div>
      <Table celled padded>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell
              singleLine
              onClick={() => {
                toogleSort("score");
              }}
            >
              Score
              <Icon name={`angle ${sortState["score"]}`} />
            </Table.HeaderCell>
            <Table.HeaderCell>Usuário</Table.HeaderCell>
            <Table.HeaderCell>Texto</Table.HeaderCell>
            <Table.HeaderCell
              singleLine
              onClick={() => {
                toogleSort("retweets");
              }}
            >
              Retweets
              <Icon name={`angle ${sortState["retweets"]}`} />
            </Table.HeaderCell>
            <Table.HeaderCell>Criado em</Table.HeaderCell>
            <Table.HeaderCell>#</Table.HeaderCell>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {tweets.map((tweet) => (
            <Table.Row key={tweet._id}>
              <Table.Cell>
                <Header as="h2" textAlign="center">
                  <Label as="a" color="red" ribbon>
                    {tweet.score.toFixed(4) * 100}%
                  </Label>
                </Header>
              </Table.Cell>
              <Table.Cell singleLine>
                <a
                  target="_blank"
                  href={`https://twitter.com/${tweet.user?.username}`}
                  rel="noreferrer"
                >
                  {tweet.user?.name?.trim()} (@{tweet.user?.username?.trim()})
                </a>
              </Table.Cell>
              <Table.Cell>
                {" "}
                <div
                  dangerouslySetInnerHTML={{
                    __html: convertHashtags(convertUsers(tweet.text)),
                  }}
                ></div>
              </Table.Cell>

              <Table.Cell textAlign="left">{tweet.retweet_count}</Table.Cell>
              <Table.Cell textAlign="left">
                {format(new Date(tweet.created_at), "dd/MM/yyyy")}
              </Table.Cell>
              <Table.Cell singleLine>
                <Button
                  as="a"
                  circular
                  color="twitter"
                  icon="twitter"
                  target="_blank"
                  href={`https://twitter.com/${tweet.user?.id}/status/${tweet.id}`}
                />
                {tweet.political == null && (
                  <Button
                    as="a"
                    circular
                    color="red"
                    icon="thumbs down"
                    onClick={() =>
                      relabel(tweet._id, "nonpolitical", tweet.text)
                    }
                  />
                )}
                {tweet.political == null && (
                  <Button
                    as="a"
                    circular
                    color="green"
                    icon="thumbs up"
                    onClick={() => relabel(tweet._id, "political", tweet.text)}
                  />
                )}
                {tweet.political == null && (
                  <Button
                    as="a"
                    circular
                    color="blue"
                    icon="question circle"
                    onClick={() => relabel(tweet._id, "quarantine", tweet.text)}
                  />
                )}
                <Button
                  as="a"
                  circular
                  color="twitter"
                  icon="list"
                  onClick={() => navigate(`/tweet/${tweet.id}`)}
                />
                {tweet.political !== null && (
                  <Button
                    as="a"
                    circular
                    color="teal"
                    icon="undo"
                    onClick={() => relabel(tweet._id, null, tweet.text)}
                  />
                )}
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
      {!loading && tweets.length == 0 && (
        <Message info>
          <Message.Header>
            Nenhum registro encontrado para esta combinação de filtros!
          </Message.Header>
          <p>Ajuste os parâmetros do seu filtro.</p>
        </Message>
      )}
      {!loading && tweets.length == 0 && (
        <Grid
          textAlign="center"
          style={{ height: "50vh" }}
          verticalAlign="middle"
        >
          <Grid.Column style={{ maxWidth: 450 }}>
            <Button
              color="teal"
              onClick={() => eventBus.dispatch("searchOpen")}
            >
              <Icon name="search" />
              Clique aqui para buscar registros
            </Button>
          </Grid.Column>
        </Grid>
      )}
    </div>
  );
};

ListTable.propTypes = {
  tweets: PropTypes.array.isRequired,
  relabel: PropTypes.func.isRequired,
  loading: PropTypes.bool.isRequired,
};

export default ListTable;
