import praw
import pandas as pd
from datetime import datetime
from googletrans import Translator

# Reddit API 접속 정보 설정하기
reddit = praw.Reddit(
    client_id="GIXRHuHR2PpbKrYwSCN_Gw",        # 이미지에 보이는 client_id
    client_secret="HeQDAMbOAByqRIvTYlKCk_wkQ8XVXw",  # 이미지에 보이는 secret
    user_agent="post_scraper/1.0 (by /u/sojung_dev)"  # 너의 앱 이름과 사용자명
)

# 번역기 초기화
translator = Translator()

def get_subreddit_posts(subreddit_name, post_limit=50, post_type='hot'):
    """서브레딧의 게시물을 가져오는 함수"""
    print(f"{post_type} 게시물 수집 시작...")  # 진행 상황 표시
    subreddit = reddit.subreddit(subreddit_name)
    
    # 게시물 종류 선택하기 (인기순/최신순/상위권)
    if post_type == 'hot':
        posts = subreddit.hot(limit=post_limit)
    elif post_type == 'new':
        posts = subreddit.new(limit=post_limit)
    elif post_type == 'top':
        posts = subreddit.top(limit=post_limit, time_filter='month')  # 한달 기준
    
    post_data = []
    for i, post in enumerate(posts, 1):
        print(f"게시물 {i}/{post_limit} 처리 중...")  # 진행 상황 표시
        # 게시물이 삭제되지 않았는지 확인
        if not post.removed_by_category:
            # 작성시간을 한국 형식으로 변환
            created_time = datetime.fromtimestamp(post.created_utc)
            formatted_time = created_time.strftime("%y.%-m.%-d %p %-I:%M")\
                .replace("AM", "오전").replace("PM", "오후")
            
            # 제목과 내용 번역하기
            try:
                translated_title = translator.translate(post.title, dest='ko').text
                translated_content = translator.translate(post.selftext, dest='ko').text if post.selftext else ''
            except Exception as e:
                print(f"번역 중 오류 발생: {e}")
                translated_title = post.title
                translated_content = post.selftext
            
            data = {
                '제목': translated_title,  # 번역된 제목
                '원본제목': post.title,    # 원본 제목도 저장
                '작성자': post.author.name if post.author else '[삭제됨]',
                '작성시간': formatted_time,
                '추천수': post.score,
                '댓글수': post.num_comments,
                '내용': translated_content,  # 번역된 내용
                '원본내용': post.selftext,   # 원본 내용도 저장
                'URL': f'https://reddit.com{post.permalink}',
            }
            # 알고트레이딩 관련 키워드가 있는 게시물만 저장
            keywords = ['algorithm', 'trading', 'strategy', 'backtest', 'python']
            if any(keyword in post.title.lower() or 
                  keyword in post.selftext.lower() for keyword in keywords):
                post_data.append(data)
    
    return pd.DataFrame(post_data)

# 메인 실행 코드
if __name__ == "__main__":
    # 게시물 수 줄이기
    hot_posts = get_subreddit_posts('algotrading', post_limit=20, post_type='hot')
    new_posts = get_subreddit_posts('algotrading', post_limit=10, post_type='new')
    top_posts = get_subreddit_posts('algotrading', post_limit=10, post_type='top')
    
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
