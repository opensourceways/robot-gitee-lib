package giteeclient

import (
	"sort"
	"time"

	sdk "github.com/opensourceways/go-gitee/gitee"
)

type BotComment struct {
	CommentID int32
	Body      string
	CreatedAt time.Time
}

func (c BotComment) IsAvailable() bool {
	return c.Body != ""
}

func FindBotComment(
	allComments []sdk.PullRequestComments,
	botName string, isTargetComment func(string) bool,
) []BotComment {
	r := make([]BotComment, 0, len(allComments))

	for i := range allComments {
		item := &allComments[i]

		if item.User.GetLogin() != botName {
			continue
		}

		if isTargetComment(item.Body) {
			ut, err := time.Parse(time.RFC3339, item.UpdatedAt)
			if err != nil {
				// it is a invalid comment if parsing time failed
				continue
			}

			r = append(r, BotComment{
				CommentID: item.Id,
				Body:      item.Body,
				CreatedAt: ut,
			})
		}
	}
	return r
}

func SortBotComments(c []BotComment) {
	if len(c) > 1 {
		sort.SliceStable(c, func(i, j int) bool {
			return c[i].CreatedAt.Before(c[j].CreatedAt)
		})
	}
}
