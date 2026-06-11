package main

import (
  "os"
  "log"
  "fmt"
  "strconv"
  "ttd"
)

const (
  APIKeyEnvVar = "TTD_API_KEY"
)

func main() {
  logger := log.New(os.Stdout, "", 0)
  apiKey := os.Getenv(APIKeyEnvVar)
  if len(apiKey) == 0 {
    logger.Fatalln("No environment variable " + APIKeyEnvVar)
  }

  if len(os.Args) < 3 || os.Args[1] != "-id" {
    help()
    return
  }

  id, err := strconv.Atoi(os.Args[2])
  if err != nil {
    fmt.Println("Invalid ID")
    return
  }

  api := ttd.NewAPI(apiKey)
  level, err := ttd.NewLevel(id, api, logger)
  if err != nil {
    logger.Fatalln(err)
  }

  level.Run()
}

func help() {
  fmt.Printf("Usage: %s -id [id]\n", os.Args[0])
}
