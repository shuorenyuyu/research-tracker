"""Comprehensive tests for daily_scheduler to reach 99% coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock dependencies
sys.modules['arxiv'] = Mock()
scholarly_mock = Mock()
sys.modules['scholarly'] = scholarly_mock
sys.modules['apscheduler'] = Mock()
sys.modules['apscheduler.schedulers'] = Mock()
sys.modules['apscheduler.schedulers.background'] = Mock()
sys.modules['apscheduler.triggers'] = Mock()
sys.modules['apscheduler.triggers.cron'] = Mock()

from src.scheduler.daily_scheduler import DailyPaperScheduler, main


class TestSchedulerStart:
    """Test scheduler start method and cron configuration"""
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    @patch('src.scheduler.daily_scheduler.BackgroundScheduler')
    @patch('src.scheduler.daily_scheduler.CronTrigger')
    def test_start_with_default_time(self, mock_cron, mock_scheduler_class, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test starting scheduler with default time"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        mock_repo_instance = Mock()
        mock_repo_instance.count_all.return_value = 10
        mock_repo_instance.count_unprocessed.return_value = 5
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = []
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        # Simulate KeyboardInterrupt after scheduler.start() is called
        mock_scheduler_instance.start.side_effect = KeyboardInterrupt()
        
        try:
            scheduler.start()
        except:
            pass
        
        # Verify add_job was called with correct params
        mock_scheduler_instance.add_job.assert_called_once()
        call_args = mock_scheduler_instance.add_job.call_args
        assert call_args is not None
        
        # Verify initial fetch was attempted
        mock_ss_instance.get_recent_papers.assert_called()
        
        # Verify shutdown was called
        mock_scheduler_instance.shutdown.assert_called_once()
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    @patch('src.scheduler.daily_scheduler.BackgroundScheduler')
    @patch('src.scheduler.daily_scheduler.CronTrigger')
    def test_start_with_custom_time(self, mock_cron, mock_scheduler_class, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test starting scheduler with custom time and timezone"""
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        mock_repo_instance = Mock()
        mock_repo_instance.count_all.return_value = 10
        mock_repo_instance.count_unprocessed.return_value = 5
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = []
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        # Simulate KeyboardInterrupt
        mock_scheduler_instance.start.side_effect = KeyboardInterrupt()
        
        try:
            scheduler.start(schedule_time="14:30", timezone="America/New_York")
        except:
            pass
        
        # Verify add_job called with correct time
        call_args = mock_scheduler_instance.add_job.call_args
        assert call_args is not None
        
        # Verify CronTrigger was used
        mock_cron.assert_called_once()
        cron_args = mock_cron.call_args
        assert cron_args[1]['hour'] == 14
        assert cron_args[1]['minute'] == 30
        assert cron_args[1]['timezone'] == "America/New_York"
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    @patch('src.scheduler.daily_scheduler.BackgroundScheduler')
    @patch('src.scheduler.daily_scheduler.CronTrigger')
    def test_start_with_exception(self, mock_cron, mock_scheduler_class, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test scheduler.start() handling exceptions"""
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        
        # Make fetch raise an exception, but start() should still set up the job
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.side_effect = Exception("Fetch error")
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        # start() should catch exception during initial fetch
        mock_scheduler_instance.start.side_effect = KeyboardInterrupt()
        
        try:
            scheduler.start()
        except:
            pass  # Expected to fail during initial fetch but still set up job
        
        # Job should still be added even if initial fetch fails
        mock_scheduler_instance.add_job.assert_called_once()
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    @patch('src.scheduler.daily_scheduler.BackgroundScheduler')
    @patch('src.scheduler.daily_scheduler.CronTrigger')
    def test_start_system_exit(self, mock_cron, mock_scheduler_class, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test scheduler handling SystemExit"""
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        mock_repo_instance = Mock()
        mock_repo_instance.count_all.return_value = 0
        mock_repo_instance.count_unprocessed.return_value = 0
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = []
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        # Simulate SystemExit
        mock_scheduler_instance.start.side_effect = SystemExit()
        
        try:
            scheduler.start()
        except SystemExit:
            pass
        
        # Verify shutdown was called
        mock_scheduler_instance.shutdown.assert_called_once()
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    @patch('src.scheduler.daily_scheduler.BackgroundScheduler')
    @patch('src.scheduler.daily_scheduler.CronTrigger')
    def test_start_scheduler_error(self, mock_cron, mock_scheduler_class, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test scheduler handling error during start"""
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        mock_repo_instance = Mock()
        mock_repo_instance.count_all.return_value = 0
        mock_repo_instance.count_unprocessed.return_value = 0
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = []
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        # Simulate exception during scheduler.start()
        mock_scheduler_instance.start.side_effect = RuntimeError("Scheduler error")
        
        with pytest.raises(RuntimeError):
            scheduler.start()


class TestSchedulerFetchExceptions:
    """Test exception handling in fetch_and_store_papers"""
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    def test_fetch_storage_exception(self, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test handling exception when storing paper"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        mock_repo_instance = Mock()
        mock_repo_instance.get_by_paper_id.return_value = None  # Paper doesn't exist
        mock_repo_instance.add_paper.side_effect = Exception("Database error")
        mock_repo_instance.count_all.return_value = 10
        mock_repo_instance.count_unprocessed.return_value = 5
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = [
            {
                'paper_id': 'test123',
                'title': 'Test Paper',
                'citation_count': 50
            }
        ]
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        # Should handle exception gracefully
        new_count, dup_count = scheduler.fetch_and_store_papers()
        
        # No papers should be added due to error
        assert new_count == 0
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    def test_fetch_top_level_exception(self, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test handling top-level exception in fetch"""
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.side_effect = RuntimeError("API completely broken")
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.ss_scraper = mock_ss_instance
        
        # Should raise exception
        with pytest.raises(RuntimeError):
            scheduler.fetch_and_store_papers()


class TestMainFunction:
    """Test main() function"""
    
    @patch('src.scheduler.daily_scheduler.DailyPaperScheduler')
    @patch('sys.argv', ['daily_scheduler.py'])
    def test_main_run_once(self, mock_scheduler_class):
        """Test main() with --run-once flag"""
        mock_scheduler_instance = Mock()
        mock_scheduler_instance.fetch_and_store_papers.return_value = (1, 0)
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        with patch('sys.argv', ['daily_scheduler.py', '--run-once']):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify fetch was called once
        mock_scheduler_instance.fetch_and_store_papers.assert_called_once()
        # start() should NOT be called in run-once mode
        mock_scheduler_instance.start.assert_not_called()
    
    @patch('src.scheduler.daily_scheduler.DailyPaperScheduler')
    def test_main_scheduled_mode(self, mock_scheduler_class):
        """Test main() in scheduled mode"""
        mock_scheduler_instance = Mock()
        mock_scheduler_instance.start.side_effect = KeyboardInterrupt()  # Exit immediately
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        with patch('sys.argv', ['daily_scheduler.py']):
            try:
                main()
            except:
                pass
        
        # Verify start was called
        mock_scheduler_instance.start.assert_called_once()
