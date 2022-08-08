import PropTypes from "prop-types";
import styled from "styled-components";
export const LinkPreview = ({ domain }) => {
  return (
    <Container>
      <ImageCover>
        <Image src={domain.preview?.image} />
      </ImageCover>
      <Info>
        <InfoContainer>
          <LinkPreviewTitle>{domain.preview?.title}</LinkPreviewTitle>
          <LinkPreviewContent>{domain.preview?.description}</LinkPreviewContent>
          <LinkPreviewDomain>
            <LinkDate>&#x1F4C5;</LinkDate>&nbsp;{domain.preview?.access_date}
            <LinkUrl>&#x1F517;</LinkUrl>&nbsp;{domain.preview?.link}
          </LinkPreviewDomain>
        </InfoContainer>
      </Info>
    </Container>
  );
};

LinkPreview.propTypes = {
  domain: PropTypes.object.isRequired,
};

const Container = styled.div`
  margin-left: auto;
  margin-right: auto;
  border-radius: 10px;
  overflow: hidden;
  width: 90%;
  margin: 10px;
`;

const ImageCover = styled.div`
  float: left;
  width: 18%;
`;

const Image = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const Info = styled.div`
  float: left;
  width: 80%;
  padding-top: 0px;
`;

const InfoContainer = styled.div`
  display: block;
  height: 100%;
  padding-left: 10px;
`;

const LinkPreviewTitle = styled.div`
  display: block;
  margin-right: auto;
  width: 98%;
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #101010;
  text-decoration: underline;
`;

const LinkPreviewContent = styled.div`
  display: block;
  font-size: small;
  height: 58%;
  overflow: auto;
  color: #606060;
`;

const LinkPreviewDomain = styled.div`
  padding-right: 2%;
  display: block;
  font-weight: bold;
  color: #808080;
  text-align: right;
  font-size: 80%;
  font-family: Arial, Helvetica, sans-serif;
`;

const LinkDate = styled.span`
  font-size: 80%;
`;

const LinkUrl = styled.span`
  font-size: 80%;
  font-size: 80%;
  margin-left: 20px;
`;
