package ttd

import (
  "net/url"
  "net/http"
  "io/ioutil"
  "strconv"
  "encoding/hex"
)

const (
  BaseURL = "http://api.trytodecrypt.com"
  EncryptPath = "/encrypt"
  SolvePath = "/solve"
)

type TTD struct {
  key string
  client http.Client
}

func NewAPI(key string) TTD {
  return TTD{
    key: key,
    client: http.Client{},
  }
}

func (ttd *TTD) request(path string, values url.Values) ([]byte, error) {
  requestURL, err := url.Parse(BaseURL)
  if err != nil {
    return nil, err
  }

  values.Add("key", ttd.key)
  requestURL.RawQuery = values.Encode()
  requestURL.Path = path
  res, err := ttd.client.Get(requestURL.String())
  if err != nil {
    return nil, err
  }

  defer res.Body.Close()
  body, err := ioutil.ReadAll(res.Body)
  if err != nil {
    return nil, err
  }

  return body, nil
}

func (ttd *TTD) Encrypt(id int, text string) ([]byte, error) {
  res, err := ttd.request(
    EncryptPath,
    url.Values{
      "id": {strconv.Itoa(id)},
      "text": {text},
    },
  )

  if err != nil {
    return nil, err
  }

  data, err := hex.DecodeString(string(res))
  if err != nil {
    return nil, err
  }

  return data, nil
}

func (ttd *TTD) Solve(id int, solution []byte) (bool, error) {
  res, err := ttd.request(
    SolvePath,
    url.Values{
      "id": {strconv.Itoa(id)},
      "solution": {string(solution)},
    },
  )

  if err != nil {
    return false, err
  }

  return string(res) == "1", nil
}
