import React from "react";

import { Card, Icon, Label, Grid, Button, Image } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useNavigate } from "@reach/router";
import { format } from "date-fns";
const ListCard = ({ tweets, relabel }) => {
  const navigate = useNavigate();
  const convertHashtags = (text) => {
    return text.replace(
      /(^|\s)(#[a-z\d-]+)/gi,
      "$1<a href='https://twitter.com/search?q=$2' target='_blank'>$2</a>"
    );
  };

  const convertUsers = (text) => {
    return text.replace(
      /(^|\s)(@[a-z\d-_]+)/gi,
      "$1<a href='https://twitter.com/$2' target='_blank'>$2</a>"
    );
  };

  return (
    <Grid stackable columns={4} padded>
      {tweets.map((tweet) => (
        <Grid.Column key={tweet._id}>
          <Card fluid>
            {tweet.media && <Image src={tweet.media[0]} wrapped ui={false} />}
            <Card.Content>
              <Card.Header>
                <Label as="h3" color="red" ribbon>
                  {tweet.score * 100}%
                </Label>
                <a href="#" position="right">
                  <Icon name="twitter" />
                </a>
                <a
                  target="_blank"
                  href={`https://twitter.com/${tweet.user?.username}`}
                  rel="noreferrer"
                >
                  {tweet.user?.name} (@{tweet.user?.username})
                </a>
              </Card.Header>
              <Card.Meta>
                <span className="date">
                  Postado em{" "}
                  {format(new Date(tweet.created_at), "dd/MM/yyyy hh:mm")}h
                </span>
              </Card.Meta>
              <Card.Description>
                <div
                  dangerouslySetInnerHTML={{
                    __html: convertHashtags(convertUsers(tweet.text)),
                  }}
                ></div>
              </Card.Description>
            </Card.Content>
            <Card.Content extra>
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
                color="twitter"
                icon="list"
                onClick={() => navigate(`/tweet/${tweet.id}`)}
              />
              <Button
                as="a"
                circular
                color="red"
                icon="thumbs down"
                onClick={() => relabel(tweet._id, "nonpolitical")}
              />
              <Button
                as="a"
                circular
                color="green"
                icon="thumbs up"
                onClick={() => relabel(tweet._id, "political")}
              />
              <Button
                as="a"
                circular
                color="blue"
                icon="question circle"
                onClick={() => relabel(tweet._id, "quarantine")}
              />

              <a>
                <Icon name="share" />
                {tweet?.retweet_count}{" "}
              </a>
              <a>
                <Icon name="chat" />
                {tweet?.reply_count}{" "}
              </a>
              <a>
                <Icon name="like" />
                {tweet?.like_count}{" "}
              </a>
            </Card.Content>
          </Card>
        </Grid.Column>
      ))}
    </Grid>
  );
};

ListCard.propTypes = {
  tweets: PropTypes.array.isRequired,
  relabel: PropTypes.func.isRequired,
};

export default ListCard;
