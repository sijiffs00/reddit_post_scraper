import praw
import pandas as pd
from datetime import datetime

# Reddit API 접속 정보 설정하기
reddit = praw.Reddit(
    client_id="GIXRHuHR2PpbKrYwSCN_Gw",        # 이미지에 보이는 client_id
    client_secret="HeQDAMbOAByqRIvTYlKCk_wkQ8XVXw",  # 이미지에 보이는 secret
    user_agent="post_scraper/1.0 (by /u/sojung_dev)"  # 너의 앱 이름과 사용자명
)

def get_subreddit_posts(subreddit_name, post_limit=50, post_type='hot'):
    """서브레딧의 게시물을 가져오는 함수"""
    subreddit = reddit.subreddit(subreddit_name)
    
    # 게시물 종류 선택하기 (인기순/최신순/상위권)
    if post_type == 'hot':
        posts = subreddit.hot(limit=post_limit)
    elif post_type == 'new':
        posts = subreddit.new(limit=post_limit)
    elif post_type == 'top':
        posts = subreddit.top(limit=post_limit, time_filter='month')  # 한달 기준
    
    post_data = []
    for post in posts:
        # 게시물이 삭제되지 않았는지 확인
        if not post.removed_by_category:
            data = {
                '제목': post.title,
                '작성자': post.author.name if post.author else '[삭제됨]',
                '작성시간': datetime.fromtimestamp(post.created_utc),
                '추천수': post.score,
                '댓글수': post.num_comments,
                '내용': post.selftext,
                'URL': f'https://reddit.com{post.permalink}',
                '플레어': post.link_flair_text,  # 게시물 태그
                '업로드_비율': post.upvote_ratio  # 추천 비율
            }
            # 알고트레이딩 관련 키워드가 있는 게시물만 저장
            keywords = ['algorithm', 'trading', 'strategy', 'backtest', 'python']
            if any(keyword in post.title.lower() or 
                  keyword in post.selftext.lower() for keyword in keywords):
                post_data.append(data)
    
    return pd.DataFrame(post_data)

# 메인 실행 코드
if __name__ == "__main__":
    # 여러 종류의 게시물 가져오기
    hot_posts = get_subreddit_posts('algotrading', post_limit=50, post_type='hot')
    new_posts = get_subreddit_posts('algotrading', post_limit=30, post_type='new')
    top_posts = get_subreddit_posts('algotrading', post_limit=20, post_type='top')
    
    # 모든 데이터 합치기
    all_posts = pd.concat([hot_posts, new_posts, top_posts])
    all_posts = all_posts.drop_duplicates(subset=['URL'])  # 중복 제거
    
    # CSV 파일로 저장하기
    filename = f'algotrading_posts_{datetime.now().strftime("%Y%m%d")}.csv'
    all_posts.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"데이터 수집 완료! '{filename}' 파일을 확인해보세요.")
    print(f"총 {len(all_posts)}개의 게시물을 수집했어요!")

# 연결이 잘 되었는지 테스트
subreddit = reddit.subreddit('algotrading')
for post in subreddit.hot(limit=3):  # 인기 게시물 3개만 가져와보기
    print(f"\n제목: {post.title}")
    print(f"작성자: {post.author}")
    print(f"추천수: {post.score}")
    print("-" * 50)
