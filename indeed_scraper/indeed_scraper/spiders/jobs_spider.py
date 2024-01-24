import re
import json
import scrapy
from urllib.parse import urlencode
from bs4 import BeautifulSoup

class IndeedJobSpider(scrapy.Spider):
    name = "indeed_jobs"
    custom_settings = {
        'FEEDS': { 'data/%(name)s_%(time)s.csv': { 'format': 'csv',}}
    }

    def get_indeed_search_url(self, keyword, location, offset=0):
        parameters = {"q": keyword, "l": location, "start": offset}
        return "https://sg.indeed.com/jobs?" + urlencode(parameters)

    def start_requests(self):
        keyword = "software engineer"
        location = "Singapore"
        indeed_jobs_url = self.get_indeed_search_url(keyword, location)
        yield scrapy.Request(url=indeed_jobs_url, callback=self.parse_search_results, meta={'keyword': keyword, 'location': location, 'offset': 0})

    def parse_search_results(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword'] 
        offset = response.meta['offset'] 
        parameters = { "q": keyword, "l": location }
        script_tag  = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag:
            print("The length of script tag is " + str(len(script_tag)))
            json_blob = json.loads(script_tag[0])

            ## Extract Jobs From Search Page
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']

            for index, job in enumerate(jobs_list):
    
                if job.get('jobkey') is not None:
                    job_url = 'https://sg.indeed.com/viewjob?jk=' + job.get('jobkey') + "&" + urlencode(parameters)
                    print(job_url)
                    yield scrapy.Request(url=job_url, 
                            callback=self.parse_job, 
                            meta={
                                'keyword': keyword, 
                                'location': location, 
                                'page': round(offset / 10) + 1 if offset > 0 else 1,
                                'position': index,
                                'jobKey': job.get('jobkey'),
                            })
                    
            # Paginate Through Jobs Pages
            if offset == 0:
                num_results = 50
                
                for offset in range(10, num_results + 10, 10):
                    url = self.get_indeed_search_url(keyword, location, offset)
                    print(offset)
                    yield scrapy.Request(url=url, callback=self.parse_search_results, meta={'keyword': keyword, 'location': location, 'offset': offset})

    def parse_job(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword'] 
        page = response.meta['page'] 
        position = response.meta['position'] 
        script_tag  = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag is not None:
            print("parsing")
            json_blob = json.loads(script_tag[0])
            # desc = response.xpath("//*[@id='jobDescriptionText']").get()
            # desc = json_blob["hostQueryExecutionResult"]["data"]["jobData"]["results"][0]["job"]["description"]['text']

            desc = json_blob["jobInfoWrapperModel"]["jobInfoModel"]["sanitizedJobDescription"]
            print(type(desc))
            desc_bs = BeautifulSoup(desc,features="lxml")
            clean_desc = desc_bs.get_text()
            job_title = json_blob["jobTitle"]
            yield {
                'keyword': keyword,
                'location': location,
                # 'page': page,
                # 'position': position,
                'jobkey': response.meta['jobKey'],
                'jobTitle': job_title,
                'jobDescription': clean_desc,
            }

    
